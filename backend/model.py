from functools import lru_cache
from pathlib import Path
from typing import Any
import os

import joblib


BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = Path(os.environ.get("MODEL_PATH", str(BASE_DIR / "sentiment_model.pkl")))
VECTORIZER_PATH = Path(os.environ.get("VECTORIZER_PATH", str(BASE_DIR / "vectorizer.pkl")))


class ModelNotAvailableError(RuntimeError):
    """Raised when the trained model artifacts are missing or cannot be loaded."""


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[Any, Any]:
    missing_paths = [
        str(path)
        for path in (MODEL_PATH, VECTORIZER_PATH)
        if not path.exists()
    ]
    if missing_paths:
        raise ModelNotAvailableError(
            "Model artifacts are missing: " + ", ".join(missing_paths)
        )

    try:
        return joblib.load(MODEL_PATH), joblib.load(VECTORIZER_PATH)
    except Exception as exc:
        raise ModelNotAvailableError(f"Could not load model artifacts: {exc}") from exc


def predict_sentiment(text: str) -> dict[str, Any]:
    model, vectorizer = load_artifacts()
    text_vector = vectorizer.transform([text])
    prediction = int(model.predict(text_vector)[0])
    sentiment = "positive" if prediction == 1 else "negative"

    probabilities = None
    confidence = None
    if hasattr(model, "predict_proba"):
        raw_probabilities = model.predict_proba(text_vector)[0]
        probabilities_by_class = {
            int(label): float(probability)
            for label, probability in zip(model.classes_, raw_probabilities)
        }
        probabilities = {
            "negative": probabilities_by_class.get(0, 0.0),
            "positive": probabilities_by_class.get(1, 0.0),
        }
        confidence = probabilities[sentiment]

    return {
        "sentiment": sentiment,
        "label": "Positive" if sentiment == "positive" else "Negative",
        "confidence": confidence,
        "probabilities": probabilities,
    }
