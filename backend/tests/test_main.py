import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402

client = TestClient(main.app)


@pytest.fixture(autouse=True)
def clear_rate_limit_bucket():
    original_rate_limit = main.settings.rate_limit_requests
    original_api_key = main.settings.api_key
    main.rate_limit_bucket.clear()
    yield
    main.rate_limit_bucket.clear()
    main.settings.rate_limit_requests = original_rate_limit
    main.settings.api_key = original_api_key


def test_health_reports_missing_model_when_artifacts_are_absent(monkeypatch):
    def raise_missing_model():
        raise main.ModelNotAvailableError("missing test artifacts")

    monkeypatch.setattr(main, "load_artifacts", raise_missing_model)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "model_available": False}


def test_predict_returns_structured_sentiment(monkeypatch):
    def fake_predict(text: str):
        assert text == "I love this movie"
        return {
            "sentiment": "positive",
            "label": "Positive",
            "confidence": 0.9,
            "probabilities": {"positive": 0.9, "negative": 0.1},
        }

    monkeypatch.setattr(main, "predict_sentiment", fake_predict)

    response = client.post("/api/v1/predict", json={"text": " I love this movie "})

    assert response.status_code == 200
    assert response.json() == {
        "text": "I love this movie",
        "sentiment": "positive",
        "label": "Positive",
        "confidence": 0.9,
        "probabilities": {"positive": 0.9, "negative": 0.1},
    }


def test_predict_returns_503_when_model_is_missing(monkeypatch):
    def raise_missing_model(text: str):
        raise main.ModelNotAvailableError("missing test artifacts")

    monkeypatch.setattr(main, "predict_sentiment", raise_missing_model)

    response = client.post("/api/v1/predict", json={"text": "hello"})

    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "MODEL_NOT_READY",
            "message": "Model files not found. Train the model first with setup_model.py.",
        }
    }


def test_predict_rejects_blank_text():
    response = client.post("/api/v1/predict", json={"text": "   "})

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"


def test_predict_rate_limits_repeated_requests(monkeypatch):
    def fake_predict(text: str):
        return {
            "sentiment": "positive",
            "label": "Positive",
            "confidence": 0.9,
            "probabilities": {"positive": 0.9, "negative": 0.1},
        }

    monkeypatch.setattr(main, "predict_sentiment", fake_predict)
    monkeypatch.setattr(main.settings, "rate_limit_requests", 1)

    first_response = client.post("/api/v1/predict", json={"text": "hello"})
    second_response = client.post("/api/v1/predict", json={"text": "hello again"})

    assert first_response.status_code == 200
    assert second_response.status_code == 429
    assert second_response.json()["error"]["code"] == "RATE_LIMIT_EXCEEDED"


def test_batch_predict_returns_multiple_results(monkeypatch):
    def fake_predict(text: str):
        return {
            "sentiment": "positive" if "love" in text else "negative",
            "label": "Positive" if "love" in text else "Negative",
            "confidence": 0.8,
            "probabilities": {"positive": 0.8, "negative": 0.2},
        }

    monkeypatch.setattr(main, "predict_sentiment", fake_predict)

    response = client.post(
        "/api/v1/predict/batch",
        json={"texts": ["I love this", "I hate this"]},
    )

    assert response.status_code == 200
    assert [item["sentiment"] for item in response.json()["results"]] == [
        "positive",
        "negative",
    ]


def test_api_key_is_required_when_configured():
    main.settings.api_key = "secret"

    response = client.get("/api/v1/analytics")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


def test_model_info_reports_missing_metadata(monkeypatch):
    def raise_missing_metadata():
        raise main.ModelNotAvailableError("missing metadata")

    monkeypatch.setattr(main, "load_model_metadata", raise_missing_metadata)

    response = client.get("/api/v1/model-info")

    assert response.status_code == 200
    assert response.json() == {"model_available": False, "metadata": None}


def test_response_includes_request_id(monkeypatch):
    def fake_predict(text: str):
        return {
            "sentiment": "positive",
            "label": "Positive",
            "confidence": 0.9,
            "probabilities": {"positive": 0.9, "negative": 0.1},
        }

    monkeypatch.setattr(main, "predict_sentiment", fake_predict)

    response = client.post(
        "/api/v1/predict",
        json={"text": "hello"},
        headers={"x-request-id": "test-request"},
    )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "test-request"
