import json
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app import logging_config
from app.main import agent, app
from app.pii import hash_user_id


def _read_jsonl(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def test_chat_logs_are_enriched_and_scrubbed(monkeypatch) -> None:
    log_path = Path(f"data/test_chat_logging_{uuid.uuid4().hex}.jsonl")
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    payload = {
        "user_id": "student-123",
        "session_id": "session-step-3-4",
        "feature": "qa",
        "message": "My email is student@vinuni.edu.vn and card 4111 1111 1111 1111. What is policy?",
    }

    with TestClient(app) as client:
        response = client.post("/chat", json=payload, headers={"x-request-id": "req-test1234"})

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-test1234"
    assert response.headers["x-response-time-ms"].isdigit()

    records = _read_jsonl(log_path)
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records

    for record in api_records:
        assert record["correlation_id"] == "req-test1234"
        assert record["user_id_hash"] == hash_user_id(payload["user_id"])
        assert record["session_id"] == payload["session_id"]
        assert record["feature"] == payload["feature"]
        assert record["model"] == agent.model
        assert record["env"] == "dev"

    raw_logs = json.dumps(records)
    assert "student@vinuni.edu.vn" not in raw_logs
    assert "4111" not in raw_logs
    assert "[REDACTED_EMAIL]" in raw_logs
    assert "[REDACTED_CREDIT_CARD]" in raw_logs
