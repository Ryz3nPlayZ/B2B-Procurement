from product.procurement_engine import ProcurementEngine


def test_create_session_returns_awarded_winner():
    engine = ProcurementEngine()

    session = engine.create_session(
        {
            "product_id": "TS-200",
            "quantity": 120,
            "max_budget": 70,
            "priority": "balanced",
        }
    )

    assert session["status"] == "awarded"
    assert session["winner"]["seller_id"]
    assert len(session["quotes"]) == 3


def test_sessions_can_be_listed_and_retrieved():
    engine = ProcurementEngine()
    session = engine.create_session({"product_id": "TS-100", "quantity": 80, "max_budget": 72})

    sessions = engine.list_sessions()
    loaded = engine.get_session(session["session_id"])

    assert len(sessions) == 1
    assert loaded is not None
    assert loaded["session_id"] == session["session_id"]
