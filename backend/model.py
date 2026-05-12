import json
from functools import lru_cache
from typing import Any

import joblib
from settings import get_settings

settings = get_settings()


class ModelNotAvailableError(RuntimeError):
    """Raised when the trained model artifacts are missing or cannot be loaded."""


@lru_cache(maxsize=1)
def load_artifacts() -> tuple[Any, Any]:
    missing_paths = [
        str(path)
        for path in (settings.model_path, settings.vectorizer_path)
        if not path.exists()
    ]
    if missing_paths:
        raise ModelNotAvailableError(
            "Model artifacts are missing: " + ", ".join(missing_paths)
        )

    try:
        return joblib.load(settings.model_path), joblib.load(settings.vectorizer_path)
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
            for label, probability in zip(
                model.classes_, raw_probabilities, strict=True
            )
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


def load_model_metadata() -> dict[str, Any]:
    if not settings.metadata_path.exists():
        raise ModelNotAvailableError(
            f"Model metadata file is missing: {settings.metadata_path}"
        )

    try:
        return json.loads(settings.metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ModelNotAvailableError(f"Could not load model metadata: {exc}") from exc
