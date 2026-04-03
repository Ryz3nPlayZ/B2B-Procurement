from __future__ import annotations

import asyncio
from collections import deque
from typing import Deque

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from product import ProcurementEngine


class RFQRequest(BaseModel):
    product_id: str = Field(default="TS-100", min_length=2)
    quantity: int = Field(default=100, ge=1)
    max_budget: float = Field(default=75.0, gt=0)
    priority: str = Field(default="balanced", pattern="^(balanced|cost|quality)$")


app = FastAPI(title="Procurement Copilot", version="2.1.0")
templates = Jinja2Templates(directory="ui/templates")
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

engine = ProcurementEngine()
event_stream: Deque[dict] = deque(maxlen=500)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "procurement-copilot"}


@app.get("/api/metrics")
async def metrics() -> dict:
    sessions = engine.list_sessions()
    if not sessions:
        return {
            "sessions": 0,
            "average_award_price": 0,
            "awarded_today": 0,
            "top_priority": "balanced",
        }

    avg_price = sum(s["winner"]["final_price"] for s in sessions) / len(sessions)
    priorities: dict[str, int] = {}
    for s in sessions:
        p = s["rfq"]["priority"]
        priorities[p] = priorities.get(p, 0) + 1

    top_priority = sorted(priorities.items(), key=lambda item: item[1], reverse=True)[0][0]
    return {
        "sessions": len(sessions),
        "average_award_price": round(avg_price, 2),
        "awarded_today": len(sessions),
        "top_priority": top_priority,
    }


@app.post("/api/sessions")
async def create_session(rfq: RFQRequest) -> dict:
    session = engine.create_session(rfq.model_dump())

    for milestone in session["milestones"]:
        event_stream.append(
            {
                "session_id": session["session_id"],
                "event": milestone["type"],
                "note": milestone["note"],
                "timestamp": milestone["at"],
            }
        )

    winner = session["winner"]
    event_stream.append(
        {
            "session_id": session["session_id"],
            "event": "award_summary",
            "note": f"Winner: {winner['seller_id']} (${winner['final_price']:.2f}/unit)",
            "timestamp": session["created_at"],
        }
    )
    return session


@app.get("/api/sessions")
async def list_sessions() -> list[dict]:
    return engine.list_sessions()


@app.get("/api/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    session = engine.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.websocket("/ws/events")
async def ws_events(websocket: WebSocket) -> None:
    await websocket.accept()
    cursor = 0
    try:
        while True:
            events = list(event_stream)
            if cursor < len(events):
                for event in events[cursor:]:
                    await websocket.send_json(event)
                cursor = len(events)
            await asyncio.sleep(0.4)
    except WebSocketDisconnect:
        return


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
