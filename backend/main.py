from pathlib import Path
import logging
import os
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from model import ModelNotAvailableError, load_artifacts, predict_sentiment


logger = logging.getLogger(__name__)
BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


def get_allowed_origins() -> list[str]:
    origins = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


app = FastAPI(title="Sentiment Analyzer API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class InputText(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


class PredictionResponse(BaseModel):
    text: str
    sentiment: Literal["positive", "negative"]
    label: str
    confidence: float | None = None
    probabilities: dict[str, float] | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_available: bool


@app.get("/health", response_model=HealthResponse)
def health_check():
    try:
        load_artifacts()
        model_available = True
    except ModelNotAvailableError as exc:
        logger.warning("Model health check failed: %s", exc)
        model_available = False

    return {"status": "ok", "model_available": model_available}


@app.post("/predict", response_model=PredictionResponse)
def predict(data: InputText):
    try:
        prediction = predict_sentiment(data.text.strip())
    except ModelNotAvailableError as exc:
        logger.warning("Prediction requested before model is available: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Model files not found. Train the model first with setup_model.py.",
        ) from exc

    return {"text": data.text.strip(), **prediction}


@app.get("/")
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Sentiment Analyzer API</h1><p><a href='/docs'>API Docs</a></p>")


if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
