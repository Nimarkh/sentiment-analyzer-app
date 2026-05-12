from pathlib import Path
import sys

from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

import main  # noqa: E402


client = TestClient(main.app)


def test_health_reports_missing_model_when_artifacts_are_absent(monkeypatch):
    def raise_missing_model():
        raise main.ModelNotAvailableError("missing test artifacts")

    monkeypatch.setattr(main, "load_artifacts", raise_missing_model)

    response = client.get("/health")

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

    response = client.post("/predict", json={"text": " I love this movie "})

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

    response = client.post("/predict", json={"text": "hello"})

    assert response.status_code == 503
    assert response.json()["detail"] == (
        "Model files not found. Train the model first with setup_model.py."
    )
