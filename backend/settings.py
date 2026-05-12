import os
from functools import lru_cache
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _get_bool(name: str, default: bool) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _get_origins() -> list[str]:
    origins = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:4200,http://127.0.0.1:4200",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


class Settings:
    app_name = os.environ.get("APP_NAME", "Sentiment Analyzer API")
    debug = _get_bool("DEBUG", False)
    api_key = os.environ.get("API_KEY", "")
    allowed_origins = _get_origins()
    max_text_length = _get_int("MAX_TEXT_LENGTH", 5000)
    rate_limit_requests = _get_int("RATE_LIMIT_REQUESTS", 30)
    rate_limit_window_seconds = _get_int("RATE_LIMIT_WINDOW_SECONDS", 60)
    static_dir = Path(os.environ.get("STATIC_DIR", str(BASE_DIR / "static")))
    analytics_db_path = Path(
        os.environ.get("ANALYTICS_DB_PATH", str(BASE_DIR / "analytics.db"))
    )
    model_path = Path(os.environ.get("MODEL_PATH", str(BASE_DIR / "sentiment_model.pkl")))
    vectorizer_path = Path(
        os.environ.get("VECTORIZER_PATH", str(BASE_DIR / "vectorizer.pkl"))
    )
    metadata_path = Path(
        os.environ.get("MODEL_METADATA_PATH", str(BASE_DIR / "model_metadata.json"))
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
