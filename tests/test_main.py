"""
Tests for the AI Engineer API.
Run with: pytest -v      (from inside the project folder)

These tests MOCK the AI call instead of using the real Gemini API — no
quota used, tests run in under a second, results are fully predictable.
"""
from unittest.mock import patch
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


class FakeAIResponse:
    def __init__(self, text):
        self.text = text


def test_home_endpoint_lists_all_three_routes():
    response = client.get("/")
    assert response.status_code == 200
    body = response.json()
    assert "/chat" in body["endpoints"]
    assert "/classify" in body["endpoints"]
    assert "/research" in body["endpoints"]


@patch("main.call_ai_with_retry")
def test_chat_returns_ai_reply(mock_ai):
    mock_ai.return_value = FakeAIResponse("Hello! How can I help you today?")
    response = client.post("/chat", json={"message": "Hi"})
    assert response.status_code == 200
    assert response.json()["reply"] == "Hello! How can I help you today?"


@patch("main.call_ai_with_retry")
def test_classify_returns_structured_json(mock_ai):
    mock_ai.return_value = FakeAIResponse(
        '{"category": "Support", "urgency": "High", "summary": "Customer needs help with login"}'
    )
    response = client.post("/classify", json={"email_text": "I can't log in to my account!"})
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "Support"
    assert body["urgency"] == "High"


@patch("main.call_ai_with_retry")
def test_classify_handles_malformed_ai_response(mock_ai):
    """If the AI returns text that ISN'T valid JSON, this proves the system
    falls back safely with a clear error instead of crashing."""
    mock_ai.return_value = FakeAIResponse("Sorry, I'm not sure how to classify that.")
    response = client.post("/classify", json={"email_text": "Some email"})
    assert response.status_code == 200
    assert "error" in response.json()


@patch("main.call_ai_with_retry")
def test_classify_handles_missing_field(mock_ai):
    """Valid JSON, but missing a required field — Pydantic should catch this."""
    mock_ai.return_value = FakeAIResponse('{"category": "Support", "urgency": "High"}')  # no summary
    response = client.post("/classify", json={"email_text": "Some email"})
    assert response.status_code == 200
    assert "error" in response.json()


@patch("main.call_ai_with_retry")
def test_research_returns_report_with_topic_and_date(mock_ai):
    mock_ai.return_value = FakeAIResponse("Summary: ... Key facts: ... Trends: ... Conclusion: ...")
    response = client.post("/research", json={"topic": "Quantum computing"})
    assert response.status_code == 200
    body = response.json()
    assert body["topic"] == "Quantum computing"
    assert "date" in body
    assert "report" in body


@patch("main.call_ai_with_retry")
def test_chat_handles_ai_service_failure(mock_ai):
    """If the AI call fails entirely (after retries), the endpoint should
    return a clear error instead of crashing with a 500."""
    mock_ai.side_effect = Exception("503 UNAVAILABLE")
    response = client.post("/chat", json={"message": "Hi"})
    assert response.status_code == 200
    assert "error" in response.json()