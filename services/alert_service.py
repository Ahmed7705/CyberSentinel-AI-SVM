"""Alert management service."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from database.database import execute, fetch_all, fetch_one, get_cursor


def get_recent_alerts(limit: int = 20) -> list[dict]:
    return fetch_all(
        """
        SELECT a.id, a.user_id, u.username, u.full_name, a.alert_type, a.description, a.risk_score,
               a.risk_level, a.status, a.created_at, a.resolved_at
        FROM alerts a
        LEFT JOIN users u ON u.id = a.user_id
        ORDER BY a.created_at DESC
        LIMIT %s
        """,
        (limit,),
    )


def get_alert(alert_id: int) -> Optional[dict]:
    return fetch_one(
        """
        SELECT a.id, a.user_id, u.username, u.full_name, a.alert_type, a.description, a.risk_score,
               a.risk_level, a.status, a.created_at, a.resolved_at, a.metadata_json
        FROM alerts a
        LEFT JOIN users u ON u.id = a.user_id
        WHERE a.id = %s
        """,
        (alert_id,),
    )


def create_alert(
    user_id: Optional[int],
    alert_type: str,
    description: str,
    risk_score: float,
    risk_level: str,
    metadata_json: str | None = None,
) -> int:
    with get_cursor() as cur:
        cur.execute(
            """
            INSERT INTO alerts (user_id, alert_type, description, risk_score, risk_level, status, metadata_json, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (user_id, alert_type, description, risk_score, risk_level, "open", metadata_json, datetime.utcnow()),
        )
        alert_id = cur.lastrowid

    if risk_level in {"medium", "high", "critical"}:
        title = f"{risk_level.title()} risk alert: {alert_type}"
        message = description[:240]
        create_notification(user_id, title, message)

    return alert_id


def create_notification(user_id: Optional[int], title: str, message: str) -> int:
    """Added by verification to satisfy instant notifications requirement."""
    with get_cursor() as cur:
        assigned_user_id = user_id
        if assigned_user_id is None:
            cur.execute("SELECT id FROM users ORDER BY id ASC LIMIT 1")
            row = cur.fetchone()
            assigned_user_id = row["id"] if row else 1
        cur.execute(
            """
            INSERT INTO notifications (user_id, title, message, is_read, created_at)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (assigned_user_id, title, message, 0, datetime.utcnow()),
        )
        return cur.lastrowid


def resolve_alert(alert_id: int, note: str | None = None) -> int:
    return execute(
        "UPDATE alerts SET status = %s, resolved_at = %s, resolution_note = %s WHERE id = %s",
        ("resolved", datetime.utcnow(), note, alert_id),
    )


def get_user_alerts(user_id: int, limit: int = 20) -> list[dict]:
    return fetch_all(
        """
        SELECT id, alert_type, description, risk_score, risk_level, status, created_at
        FROM alerts
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (user_id, limit),
    )


def get_alert_metrics() -> dict:
    rows = fetch_all(
        """
        SELECT
            COUNT(*) AS total_alerts,
            SUM(CASE WHEN status = 'open' THEN 1 ELSE 0 END) AS open_alerts,
            SUM(CASE WHEN risk_level = 'critical' THEN 1 ELSE 0 END) AS critical_alerts,
            SUM(CASE WHEN risk_level = 'high' THEN 1 ELSE 0 END) AS high_alerts
        FROM alerts
        """
    )
    metrics = rows[0] if rows else {"total_alerts": 0, "open_alerts": 0, "critical_alerts": 0, "high_alerts": 0}
    return metrics
