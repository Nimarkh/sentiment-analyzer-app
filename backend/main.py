import logging
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Literal
from uuid import uuid4

from analytics import get_summary, init_analytics, record_prediction
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from model import (
    ModelNotAvailableError,
    load_artifacts,
    load_model_metadata,
    predict_sentiment,
)
from pydantic import BaseModel, Field, field_validator
from settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()
request_log = logging.getLogger("sentiment_analyzer.requests")
rate_limit_bucket: defaultdict[str, deque[float]] = defaultdict(deque)


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def verify_api_key(request: Request) -> None:
    if not settings.api_key:
        return

    if request.headers.get("x-api-key") == settings.api_key:
        return

    raise HTTPException(
        status_code=401,
        detail={
            "code": "UNAUTHORIZED",
            "message": "A valid x-api-key header is required.",
        },
    )


def enforce_rate_limit(request: Request) -> None:
    client_host = request.client.host if request.client else "unknown"
    now = time.monotonic()
    bucket = rate_limit_bucket[client_host]
    window_start = now - settings.rate_limit_window_seconds

    while bucket and bucket[0] < window_start:
        bucket.popleft()

    if len(bucket) >= settings.rate_limit_requests:
        raise HTTPException(
            status_code=429,
            detail={
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Too many requests. Please try again later.",
            },
        )

    bucket.append(now)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_analytics()
    yield


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    started_at = time.perf_counter()
    request_id = request.headers.get("x-request-id", str(uuid4()))
    request.state.request_id = request_id
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started_at) * 1000
    response.headers["x-request-id"] = request_id
    request_log.info(
        "%s %s -> %s %.2fms request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if isinstance(exc.detail, dict):
        code = str(exc.detail.get("code", "HTTP_ERROR"))
        message = str(exc.detail.get("message", "Request failed."))
    else:
        code = "HTTP_ERROR"
        message = str(exc.detail)
    return error_response(exc.status_code, code, message)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    first_error = exc.errors()[0] if exc.errors() else {}
    message = str(first_error.get("msg", "Invalid request payload."))
    return error_response(422, "VALIDATION_ERROR", message)


class InputText(BaseModel):
    text: str = Field(..., min_length=1, max_length=settings.max_text_length)

    @field_validator("text")
    @classmethod
    def text_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Text must not be blank.")
        return value


class BatchInputText(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=10)

    @field_validator("texts")
    @classmethod
    def texts_must_be_valid(cls, values: list[str]) -> list[str]:
        for value in values:
            if not value.strip():
                raise ValueError("Texts must not contain blank items.")
            if len(value) > settings.max_text_length:
                raise ValueError(
                    f"Each text must be at most {settings.max_text_length} characters."
                )
        return values


class PredictionResponse(BaseModel):
    text: str
    sentiment: Literal["positive", "negative"]
    label: str
    confidence: float | None = None
    probabilities: dict[str, float] | None = None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    model_available: bool


class BatchPredictionResponse(BaseModel):
    results: list[PredictionResponse]


class ModelInfoResponse(BaseModel):
    model_available: bool
    metadata: dict | None = None


class AnalyticsResponse(BaseModel):
    total_predictions: int
    by_sentiment: dict[str, int]
    average_confidence: float | None = None
    average_duration_ms: float | None = None
    recent: list[dict]


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check():
    try:
        load_artifacts()
        model_available = True
    except ModelNotAvailableError as exc:
        logger.warning("Model health check failed: %s", exc)
        model_available = False

    return {"status": "ok", "model_available": model_available}


@app.get("/health", response_model=HealthResponse)
def legacy_health_check():
    return health_check()


@app.get("/api/v1/model-info", response_model=ModelInfoResponse)
def model_info():
    try:
        metadata = load_model_metadata()
        load_artifacts()
        return {"model_available": True, "metadata": metadata}
    except ModelNotAvailableError as exc:
        logger.warning("Model info requested before model is available: %s", exc)
        return {"model_available": False, "metadata": None}


@app.get("/api/v1/analytics", response_model=AnalyticsResponse)
def analytics_summary(request: Request):
    verify_api_key(request)
    return get_summary()


@app.post("/api/v1/predict", response_model=PredictionResponse)
def predict(data: InputText, request: Request):
    verify_api_key(request)
    enforce_rate_limit(request)
    try:
        started_at = time.perf_counter()
        prediction = predict_sentiment(data.text.strip())
        duration_ms = (time.perf_counter() - started_at) * 1000
    except ModelNotAvailableError as exc:
        logger.warning("Prediction requested before model is available: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={
                "code": "MODEL_NOT_READY",
                "message": "Model files not found. Train the model first with setup_model.py.",
            },
        ) from exc

    record_prediction(data.text.strip(), prediction, duration_ms)
    return {"text": data.text.strip(), **prediction}


@app.post("/api/v1/predict/batch", response_model=BatchPredictionResponse)
def predict_batch(data: BatchInputText, request: Request):
    verify_api_key(request)
    enforce_rate_limit(request)

    results = []
    try:
        for text in data.texts:
            clean_text = text.strip()
            started_at = time.perf_counter()
            prediction = predict_sentiment(clean_text)
            duration_ms = (time.perf_counter() - started_at) * 1000
            record_prediction(clean_text, prediction, duration_ms)
            results.append({"text": clean_text, **prediction})
    except ModelNotAvailableError as exc:
        logger.warning("Batch prediction requested before model is available: %s", exc)
        raise HTTPException(
            status_code=503,
            detail={
                "code": "MODEL_NOT_READY",
                "message": "Model files not found. Train the model first with setup_model.py.",
            },
        ) from exc

    return {"results": results}


@app.post("/predict", response_model=PredictionResponse)
def legacy_predict(data: InputText, request: Request):
    return predict(data, request)


@app.get("/")
async def serve_index():
    index_path = settings.static_dir / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return HTMLResponse("<h1>Sentiment Analyzer API</h1><p><a href='/docs'>API Docs</a></p>")


if settings.static_dir.exists():
    app.mount("/", StaticFiles(directory=settings.static_dir, html=True), name="static")
