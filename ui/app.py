from fastapi import FastAPI, Request, WebSocket
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio

app = FastAPI(title="ASI Procurement Demo")
templates = Jinja2Templates(directory="ui/templates")
app.mount("/static", StaticFiles(directory="ui/static"), name="static")

negotiation_log = []

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        if negotiation_log:
            await websocket.send_json(negotiation_log[-1])
        await asyncio.sleep(0.5)

@app.post("/start-rfq")
async def start_rfq(data: dict):
    # Trigger agent negotiation
    # ... (import and run buyer_agent with params)
    return {"status": "started", "rfq_id": "rfq-001"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
