"""
test_call_api_routes.py — API Integration Tests for Phase 3 Calls Endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_call_api():
    response = client.post(
        "/api/v1/calls",
        json={"phone": "+84901234567", "lead_id": "lead_test_01", "metadata": {"source": "web_test"}}
    )
    assert response.status_code == 201
    data = response.json()
    assert "call_id" in data
    assert data["phone"] == "+84901234567"
    assert data["state"] == "QUEUED"


def test_start_call_api():
    create_res = client.post("/api/v1/calls", json={"phone": "+84901234567"})
    call_id = create_res.json()["call_id"]

    start_res = client.post(f"/api/v1/calls/{call_id}/start")
    assert start_res.status_code == 200
    assert start_res.json()["state"] == "CONNECTED"


def test_send_customer_message_api():
    create_res = client.post("/api/v1/calls", json={"phone": "+84901234567"})
    call_id = create_res.json()["call_id"]
    client.post(f"/api/v1/calls/{call_id}/start")

    msg_res = client.post(
        f"/api/v1/calls/{call_id}/message",
        json={"message": "Anh muốn mua căn hộ 2 phòng ngủ ở Quận 7, ngân sách 3 tỷ."}
    )
    assert msg_res.status_code == 200
    data = msg_res.json()
    assert "ai_text" in data
    assert "tts_payload" in data
    assert data["call_id"] == call_id


def test_trigger_interruption_api():
    create_res = client.post("/api/v1/calls", json={"phone": "+84901234567"})
    call_id = create_res.json()["call_id"]
    client.post(f"/api/v1/calls/{call_id}/start")

    int_res = client.post(
        f"/api/v1/calls/{call_id}/interrupt",
        json={"message": "Khoan em ơi, dự án này ở đâu vậy?"}
    )
    assert int_res.status_code == 200
    assert int_res.json()["interrupted"] is True


def test_get_call_events_api():
    create_res = client.post("/api/v1/calls", json={"phone": "+84901234567"})
    call_id = create_res.json()["call_id"]

    events_res = client.get(f"/api/v1/calls/{call_id}/events")
    assert events_res.status_code == 200
    data = events_res.json()
    assert data["events_count"] >= 1


def test_simulate_call_api():
    sim_res = client.post(
        "/api/v1/calls/simulate",
        json={
            "phone": "+84901234567",
            "conversation_turns": [
                "Anh muốn mua căn hộ 2PN.",
                "Ngân sách khoảng 3 tỷ.",
                "Ở Quận 7."
            ]
        }
    )
    assert sim_res.status_code == 200
    data = sim_res.json()
    assert "call_id" in data
    assert data["total_turns"] >= 3
