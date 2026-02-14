from fastapi.testclient import TestClient
import api_gateway.main as main
from api_gateway.main import app
import services.llm_service as lsvc


client = TestClient(app)


def test_health_endpoint():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_ask_endpoint_mocked(monkeypatch):
    # Ensure non-demo mode so API uses LLM service
    monkeypatch.setattr(main, "USE_DEMO_MODE", False)
    # Mock generate_answer to avoid external calls
    # The API imports `answer_question` at module import time, so patch the
    # function the API actually calls (bound in `main`) to avoid real OpenAI calls.
    monkeypatch.setattr(main, "answer_question", lambda question, k=5, use_rephrasing=False: "Mocked answer")

    r = client.post("/ask", json={"question": "test"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("answer") == "Mocked answer"
