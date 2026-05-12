import sqlite3
from datetime import UTC, datetime
from typing import Any

from settings import get_settings

settings = get_settings()


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(settings.analytics_db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_analytics() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                text_length INTEGER NOT NULL,
                sentiment TEXT NOT NULL,
                confidence REAL,
                duration_ms REAL NOT NULL
            )
            """
        )


def record_prediction(text: str, prediction: dict[str, Any], duration_ms: float) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO predictions (
                created_at,
                text_length,
                sentiment,
                confidence,
                duration_ms
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                datetime.now(UTC).isoformat(),
                len(text),
                prediction["sentiment"],
                prediction.get("confidence"),
                duration_ms,
            ),
        )


def get_summary() -> dict[str, Any]:
    with get_connection() as connection:
        total = connection.execute("SELECT COUNT(*) AS total FROM predictions").fetchone()
        by_sentiment = connection.execute(
            """
            SELECT sentiment, COUNT(*) AS count
            FROM predictions
            GROUP BY sentiment
            """
        ).fetchall()
        averages = connection.execute(
            """
            SELECT AVG(confidence) AS average_confidence,
                   AVG(duration_ms) AS average_duration_ms
            FROM predictions
            """
        ).fetchone()
        recent = connection.execute(
            """
            SELECT created_at, text_length, sentiment, confidence, duration_ms
            FROM predictions
            ORDER BY id DESC
            LIMIT 10
            """
        ).fetchall()

    return {
        "total_predictions": total["total"],
        "by_sentiment": {row["sentiment"]: row["count"] for row in by_sentiment},
        "average_confidence": averages["average_confidence"],
        "average_duration_ms": averages["average_duration_ms"],
        "recent": [dict(row) for row in recent],
    }
