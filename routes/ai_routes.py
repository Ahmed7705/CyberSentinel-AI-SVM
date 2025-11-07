"""AI orchestration routes."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable, Tuple

from flask import Blueprint, current_app, jsonify, request, session

from database.database import fetch_all, fetch_one
from ai_engine.engine import generate_alert_insight


def _get_engine():
    engine = current_app.extensions.get("ai_engine")
    if not engine:
        raise RuntimeError("AI engine is not initialised")
    return engine


ai_bp = Blueprint("ai", __name__, url_prefix="/ai")

@ai_bp.route("/detect", methods=["POST"])
def detect_activity():
    if not session.get("user_id"):
        return {"error": "Authentication required"}, 401
    payload = request.get_json() or {}
    payload.setdefault("user_id", session.get("user_id"))
    payload.setdefault("description", payload.get("event_type", "Manual scan"))
    engine = _get_engine()
    try:
        result = engine.analyse_activity(payload)
    except RuntimeError as exc:
        return {"error": str(exc)}, 400
    return jsonify(result.as_dict())


@ai_bp.route("/train", methods=["POST"])
def train_models():
    if session.get("role") != "admin":
        return {"error": "Admin access required"}, 403
    limit = int((request.get_json() or {}).get("limit", 500))
    engine = _get_engine()
    engine.warm_start(limit=limit)
    return {"status": "trained", "limit": limit}


@ai_bp.route("/activity-feed", methods=["GET"])
def activity_feed():
    if session.get("role") != "admin":
        return {"error": "Admin access required"}, 403
    rows = fetch_all(
        """
        SELECT user_id, event_type, source_ip, device, location, timestamp, risk_score
        FROM activity_logs
        ORDER BY timestamp DESC
        LIMIT 50
        """
    )
    return jsonify(rows)


@ai_bp.route("/interact", methods=["POST"])
def interact_with_ai():
    if session.get("role") != "admin":
        return {"error": "Admin access required"}, 403
    payload = request.get_json() or {}
    prompt = (payload.get("prompt") or "").strip()
    if not prompt:
        return {"error": "Prompt is required"}, 400
    insight = generate_alert_insight(prompt)
    if not insight:
        insight = "AI service is currently unavailable. Please try again later."
    return {"response": insight}


def _coerce_user_ids(raw_values: Iterable) -> list[int]:
    user_ids: list[int] = []
    if not raw_values:
        return user_ids
    for value in raw_values:
        try:
            user_ids.append(int(value))
        except (TypeError, ValueError):
            continue
    return user_ids


def _build_conditions(
    user_ids: list[int],
    start_date: str | None,
    end_date: str | None,
    alias: str,
    date_column: str,
) -> Tuple[list[str], list]:
    conditions: list[str] = []
    params: list = []

    if user_ids:
        placeholders = ", ".join(["%s"] * len(user_ids))
        conditions.append(f"{alias}.user_id IN ({placeholders})")
        params.extend(user_ids)

    if start_date:
        conditions.append(f"{alias}.{date_column} >= %s")
        params.append(f"{start_date} 00:00:00")

    if end_date:
        conditions.append(f"{alias}.{date_column} <= %s")
        params.append(f"{end_date} 23:59:59")

    return conditions, params


def _to_int(value, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_iso(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return value


@ai_bp.route("/analyze-system", methods=["POST"])
def analyze_system():
    if session.get("role") != "admin":
        return jsonify({"success": False, "error": "Admin access required"}), 403

    payload = request.get_json() or {}
    filters = payload.get("filters") or {}

    user_ids = _coerce_user_ids(filters.get("users"))
    start_date = (filters.get("start_date") or "").strip() or None
    end_date = (filters.get("end_date") or "").strip() or None
    requested_analysis = (
        payload.get("analysis_type")
        or filters.get("analysis_type")
        or "custom_analysis"
    )

    alert_conditions, alert_params = _build_conditions(
        user_ids, start_date, end_date, alias="a", date_column="created_at"
    )
    alerts_where = f"WHERE {' AND '.join(alert_conditions)}" if alert_conditions else ""

    activity_conditions, activity_params = _build_conditions(
        user_ids, start_date, end_date, alias="l", date_column="timestamp"
    )
    activity_where = (
        f"WHERE {' AND '.join(activity_conditions)}" if activity_conditions else ""
    )

    alert_stats = fetch_one(
        f"""
        SELECT
            COUNT(*) AS total_alerts,
            SUM(CASE WHEN a.risk_level IN ('high','critical') THEN 1 ELSE 0 END) AS high_alerts,
            SUM(CASE WHEN a.status = 'open' THEN 1 ELSE 0 END) AS open_alerts,
            MAX(a.created_at) AS last_alert
        FROM alerts a
        {alerts_where}
        """,
        tuple(alert_params),
    ) or {}

    activity_stats = fetch_one(
        f"""
        SELECT
            COUNT(*) AS total_events,
            AVG(l.risk_score) AS avg_risk,
            MAX(l.risk_score) AS peak_risk,
            MAX(l.timestamp) AS last_activity
        FROM activity_logs l
        {activity_where}
        """,
        tuple(activity_params),
    ) or {}

    top_events = fetch_all(
        f"""
        SELECT
            l.event_type,
            COUNT(*) AS total,
            AVG(l.risk_score) AS avg_risk
        FROM activity_logs l
        {activity_where}
        GROUP BY l.event_type
        ORDER BY total DESC
        LIMIT 5
        """,
        tuple(activity_params),
    )

    top_users = fetch_all(
        f"""
        SELECT
            u.id,
            u.full_name,
            u.username,
            COUNT(a.id) AS alert_count,
            SUM(CASE WHEN a.risk_level IN ('high','critical') THEN 1 ELSE 0 END) AS high_alerts,
            MAX(a.created_at) AS last_alert
        FROM alerts a
        JOIN users u ON u.id = a.user_id
        {alerts_where}
        GROUP BY u.id, u.full_name, u.username
        ORDER BY high_alerts DESC, alert_count DESC
        LIMIT 5
        """,
        tuple(alert_params),
    )

    recent_alerts = fetch_all(
        f"""
        SELECT
            a.id,
            a.alert_type,
            a.risk_level,
            a.risk_score,
            a.status,
            a.created_at,
            u.full_name,
            u.username
        FROM alerts a
        LEFT JOIN users u ON u.id = a.user_id
        {alerts_where}
        ORDER BY a.created_at DESC
        LIMIT 5
        """,
        tuple(alert_params),
    )

    high_risk_rows = fetch_all(
        f"""
        SELECT
            l.id,
            l.event_type,
            l.source_ip,
            l.device,
            l.timestamp,
            l.risk_score,
            u.full_name,
            u.username
        FROM activity_logs l
        LEFT JOIN users u ON u.id = l.user_id
        {activity_where}
        ORDER BY l.risk_score DESC, l.timestamp DESC
        LIMIT 5
        """,
        tuple(activity_params),
    )

    user_statistics_rows = fetch_all(
        f"""
        SELECT
            COALESCE(u.department, 'Unassigned') AS department,
            COUNT(DISTINCT u.id) AS user_count,
            COUNT(a.id) AS alert_count
        FROM alerts a
        JOIN users u ON u.id = a.user_id
        {alerts_where}
        GROUP BY COALESCE(u.department, 'Unassigned')
        ORDER BY alert_count DESC
        LIMIT 6
        """,
        tuple(alert_params),
    )

    overall_user_count = fetch_one(
        "SELECT COUNT(*) AS total_users FROM users", ()
    ) or {}

    affected_user_count = fetch_one(
        f"""
        SELECT COUNT(DISTINCT a.user_id) AS affected_users
        FROM alerts a
        {alerts_where}
        """,
        tuple(alert_params),
    ) or {}

    alert_summary = {
        "total_alerts": _to_int(alert_stats.get("total_alerts")),
        "high_alerts": _to_int(alert_stats.get("high_alerts")),
        "open_alerts": _to_int(alert_stats.get("open_alerts")),
        "last_alert": _to_iso(alert_stats.get("last_alert")),
    }

    activity_summary = {
        "total_events": _to_int(activity_stats.get("total_events")),
        "average_risk": round(_to_float(activity_stats.get("avg_risk")), 3),
        "peak_risk": round(_to_float(activity_stats.get("peak_risk")), 3),
        "last_activity": _to_iso(activity_stats.get("last_activity")),
    }

    serialised_events = [
        {
            "event_type": row.get("event_type"),
            "total": _to_int(row.get("total")),
            "average_risk": round(_to_float(row.get("avg_risk")), 3),
        }
        for row in top_events or []
    ]

    serialised_users = [
        {
            "id": row.get("id"),
            "full_name": row.get("full_name"),
            "username": row.get("username"),
            "alert_count": _to_int(row.get("alert_count")),
            "high_alerts": _to_int(row.get("high_alerts")),
            "last_alert": _to_iso(row.get("last_alert")),
        }
        for row in top_users or []
    ]

    serialised_recent_alerts = [
        {
            "id": row.get("id"),
            "alert_type": row.get("alert_type"),
            "risk_level": row.get("risk_level"),
            "risk_score": round(_to_float(row.get("risk_score")), 3),
            "status": row.get("status"),
            "created_at": _to_iso(row.get("created_at")),
            "full_name": row.get("full_name"),
            "username": row.get("username"),
        }
        for row in recent_alerts or []
    ]

    high_risk_activities = [
        {
            "id": row.get("id"),
            "full_name": row.get("full_name") or row.get("username") or "Unknown user",
            "event_type": row.get("event_type"),
            "source_ip": row.get("source_ip"),
            "device": row.get("device"),
            "timestamp": _to_iso(row.get("timestamp")),
            "risk_score": _to_float(row.get("risk_score")),
        }
        for row in high_risk_rows or []
    ]

    user_statistics = [
        {
            "department": row.get("department"),
            "user_count": _to_int(row.get("user_count")),
            "alert_count": _to_int(row.get("alert_count")),
        }
        for row in user_statistics_rows or []
    ]

    scoped_user_total = _to_int(affected_user_count.get("affected_users"))
    total_users_metric = (
        scoped_user_total
        if alert_conditions
        else _to_int(overall_user_count.get("total_users"))
    )

    metrics_summary = (
        f"Total alerts: {alert_summary['total_alerts']}, "
        f"High severity: {alert_summary['high_alerts']}, "
        f"Open alerts: {alert_summary['open_alerts']}, "
        f"Events analysed: {activity_summary['total_events']}, "
        f"Average risk score: {activity_summary['average_risk']:.3f}"
    )

    ai_prompt = (
        "Generate a concise security operations summary highlighting anomalies and recommended actions. "
        f"Analysis type: {requested_analysis}. {metrics_summary}. "
        f"Top event categories: {', '.join(str(event.get('event_type') or 'unknown') for event in serialised_events) or 'none'}. "
        f"Key accounts with high alerts: {', '.join(user.get('username') or str(user.get('id')) for user in serialised_users) or 'none'}."
    )

    insight_text = generate_alert_insight(ai_prompt)
    if not insight_text:
        insight_text = (
            "Analysis completed. No significant anomalies were detected for the selected filters."
        )

    analysis_payload = {
        "analysis_type": requested_analysis,
        "filters": {
            "users": user_ids,
            "start_date": start_date,
            "end_date": end_date,
        },
        "system_overview": {
            "total_users": total_users_metric,
            "scoped_users": scoped_user_total,
            "total_alerts": alert_summary["total_alerts"],
            "high_risk_alerts": alert_summary["high_alerts"],
            "avg_risk_score": activity_summary["average_risk"],
        },
        "high_risk_activities": high_risk_activities,
        "user_statistics": user_statistics,
        "alert_summary": alert_summary,
        "activity_summary": activity_summary,
        "top_events": serialised_events,
        "top_users": serialised_users,
        "recent_alerts": serialised_recent_alerts,
    }

    return jsonify(
        {
            "success": True,
            "analysis_data": analysis_payload,
            "ai_insights": {
                "summary": insight_text,
                "generated_at": datetime.utcnow().isoformat() + "Z",
            },
        }
    )

