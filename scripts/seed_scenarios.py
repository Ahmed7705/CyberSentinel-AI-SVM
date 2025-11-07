from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Dict, Iterable

import mysql.connector
from dotenv import load_dotenv

from app import create_app
from config import Config
from services.auth_service import hash_password
from ai_engine.engine import AIEngine

DEFAULT_PASSWORD = "CyberSentinel!23"

USERS = [
    {"username": "admin", "full_name": "Aiden Hunt", "role": "admin", "department": "Security Operations"},
    {"username": "jdoe", "full_name": "Jordan Doe", "role": "user", "department": "Finance"},
    {"username": "ssmith", "full_name": "Sloan Smith", "role": "user", "department": "HR"},
    {"username": "kwong", "full_name": "Kai Wong", "role": "user", "department": "R&D"},
    {"username": "mrobbins", "full_name": "Mila Robbins", "role": "user", "department": "IT"},
    {"username": "dpatel", "full_name": "Dev Patel", "role": "analyst", "department": "Security Operations"},
    {"username": "rtaylor", "full_name": "Riley Taylor", "role": "user", "department": "Marketing"},
    {"username": "lgarcia", "full_name": "Lena Garcia", "role": "user", "department": "Finance"},
    {"username": "bking", "full_name": "Bailey King", "role": "user", "department": "Product"},
    {"username": "cibarra", "full_name": "Carmen Ibarra", "role": "user", "department": "Legal"},
]


def _get_connection():
    load_dotenv()
    cfg = Config.mysql_config()
    return mysql.connector.connect(**cfg)


def _ensure_users(cursor) -> Dict[str, int]:
    password_hash = hash_password(DEFAULT_PASSWORD)
    username_to_id: Dict[str, int] = {}
    for user in USERS:
        cursor.execute("SELECT id FROM users WHERE username = %s", (user["username"],))
        row = cursor.fetchone()
        if row:
            user_id = row[0]
            cursor.execute(
                "UPDATE users SET full_name = %s, role = %s, department = %s, password_hash = %s, is_active = 1 WHERE id = %s",
                (user["full_name"], user["role"], user["department"], password_hash, user_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO users (username, password_hash, full_name, role, department, is_active, created_at)
                VALUES (%s, %s, %s, %s, %s, 1, %s)
                """,
                (
                    user["username"],
                    password_hash,
                    user["full_name"],
                    user["role"],
                    user["department"],
                    datetime.utcnow(),
                ),
            )
            user_id = cursor.lastrowid
        username_to_id[user["username"]] = user_id
    return username_to_id


def _activity_exists(cursor, user_id: int, event_type: str, timestamp: datetime) -> bool:
    cursor.execute(
        "SELECT id FROM activity_logs WHERE user_id = %s AND event_type = %s AND timestamp = %s LIMIT 1",
        (user_id, event_type, timestamp),
    )
    return cursor.fetchone() is not None


def _seed_activity_logs(cursor, user_ids: Dict[str, int]) -> None:
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    scenarios = [
        {
            "username": "ssmith",
            "event_type": "late_night_login",
            "source_ip": "10.0.2.18",
            "device": "Surface-Pro-HR03",
            "location": "Remote",
            "bytes_transferred": 0,
            "files_accessed": 0,
            "failed_attempts": 0,
            "session_duration": 420,
            "risk_score": 0.82,
            "timestamp": now - timedelta(days=2, hours=now.hour - 3),
        },
        {
            "username": "cibarra",
            "event_type": "late_night_login",
            "source_ip": "10.0.7.14",
            "device": "HP-Elite-LGL01",
            "location": "Remote",
            "bytes_transferred": 0,
            "files_accessed": 0,
            "failed_attempts": 0,
            "session_duration": 360,
            "risk_score": 0.76,
            "timestamp": now - timedelta(days=4, hours=now.hour - 2),
        },
        {
            "username": "bking",
            "event_type": "mass_copy",
            "source_ip": "10.0.4.77",
            "device": "MacBook-Pro-PD01",
            "location": "Remote",
            "bytes_transferred": int(1.9 * 1024 * 1024 * 1024),
            "files_accessed": 160,
            "failed_attempts": 0,
            "session_duration": 120,
            "risk_score": 0.9,
            "timestamp": now - timedelta(days=3, hours=1),
        },
        {
            "username": "kwong",
            "event_type": "privilege_escalation",
            "source_ip": "10.0.5.12",
            "device": "ThinkPad-IT09",
            "location": "NYC HQ",
            "bytes_transferred": 5242880,
            "files_accessed": 3,
            "failed_attempts": 1,
            "session_duration": 45,
            "risk_score": 0.88,
            "timestamp": now - timedelta(days=5),
        },
        {
            "username": "dpatel",
            "event_type": "remote_download",
            "source_ip": "203.0.113.88",
            "device": "Automation-VM",
            "location": "Remote",
            "bytes_transferred": int(2.1 * 1024 * 1024 * 1024),
            "files_accessed": 40,
            "failed_attempts": 0,
            "session_duration": 30,
            "risk_score": 0.85,
            "timestamp": now - timedelta(days=1, hours=2),
        },
    ]

    # Add supportive normal activity to balance training data.
    normals: Iterable[dict] = (
        {
            "username": "jdoe",
            "event_type": "login",
            "source_ip": "10.0.1.25",
            "device": "Windows-Desktop-FIN01",
            "location": "NYC HQ",
            "bytes_transferred": 0,
            "files_accessed": 0,
            "failed_attempts": 0,
            "session_duration": 480,
            "risk_score": 0.15,
            "timestamp": now - timedelta(days=idx, hours=idx % 8),
        }
        for idx in range(6)
    )

    normals_2: Iterable[dict] = (
        {
            "username": "lgarcia",
            "event_type": "file_access",
            "source_ip": "10.0.1.56",
            "device": "Dell-Latitude-FIN05",
            "location": "NYC HQ",
            "bytes_transferred": 1048576,
            "files_accessed": 4,
            "failed_attempts": 0,
            "session_duration": 240,
            "risk_score": 0.25,
            "timestamp": now - timedelta(days=idx, hours=idx % 5),
        }
        for idx in range(6)
    )

    normals_3: Iterable[dict] = (
        {
            "username": "mrobbins",
            "event_type": "login",
            "source_ip": "10.0.5.12",
            "device": "ThinkPad-IT09",
            "location": "NYC HQ",
            "bytes_transferred": 0,
            "files_accessed": 0,
            "failed_attempts": 0,
            "session_duration": 410,
            "risk_score": 0.18,
            "timestamp": now - timedelta(days=idx + 1, hours=idx % 6),
        }
        for idx in range(4)
    )

    future_activity = {
        "username": "rtaylor",
        "event_type": "login",
        "source_ip": "10.0.6.32",
        "device": "MacBook-Air-MKT02",
        "location": "Remote",
        "bytes_transferred": 0,
        "files_accessed": 0,
        "failed_attempts": 0,
        "session_duration": 300,
        "risk_score": 0.2,
        "timestamp": now + timedelta(days=7),
    }

    for entry in list(scenarios) + list(normals) + list(normals_2) + list(normals_3) + [future_activity]:
        user_id = user_ids[entry["username"]]
        if _activity_exists(cursor, user_id, entry["event_type"], entry["timestamp"]):
            continue
        cursor.execute(
            """
            INSERT INTO activity_logs (user_id, event_type, source_ip, device, location, bytes_transferred,
                                       files_accessed, failed_attempts, session_duration, risk_score, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                entry["event_type"],
                entry["source_ip"],
                entry["device"],
                entry["location"],
                entry["bytes_transferred"],
                entry["files_accessed"],
                entry["failed_attempts"],
                entry["session_duration"],
                entry["risk_score"],
                entry["timestamp"],
            ),
        )


def _run_detection() -> None:
    flask_app = create_app()
    with flask_app.app_context():
        engine: AIEngine = flask_app.extensions["ai_engine"]  # type: ignore[attr-defined]
        engine.warm_start()
        scenarios = [
            {
                "user_id": 3,
                "event_type": "late_night_login",
                "timestamp": datetime.utcnow().replace(hour=3, minute=0, second=0, microsecond=0),
                "source_ip": "10.0.2.18",
                "device": "Surface-Pro-HR03",
                "location": "Remote",
                "description": "Automated seed: late night login",
            },
            {
                "user_id": 9,
                "event_type": "mass_copy",
                "timestamp": datetime.utcnow(),
                "source_ip": "10.0.4.77",
                "device": "MacBook-Pro-PD01",
                "bytes_transferred": int(1.8 * 1024 * 1024 * 1024),
                "files_accessed": 140,
                "description": "Automated seed: mass copy",
            },
            {
                "user_id": 6,
                "event_type": "remote_download",
                "timestamp": datetime.utcnow(),
                "source_ip": "203.0.113.88",
                "device": "Automation-VM",
                "user_agent": "Python-urllib/3.13",
                "description": "Automated seed: remote script download",
            },
        ]
        for payload in scenarios:
            engine.analyse_activity(payload)


def _verify_alerts_and_notifications(cursor) -> None:
    cursor.execute(
        "SELECT COUNT(*) FROM alerts WHERE risk_score >= %s",
        (0.6,),
    )
    alerts_count = cursor.fetchone()[0]
    if alerts_count == 0:
        raise RuntimeError("Seed verification failed: expected alerts with risk_score >= 0.6")

    cursor.execute("SELECT COUNT(*) FROM notifications WHERE created_at >= %s", (datetime.utcnow() - timedelta(days=1),))
    if cursor.fetchone()[0] == 0:
        raise RuntimeError("Seed verification failed: expected notifications for recent alerts")


def seed() -> None:
    connection = _get_connection()
    try:
        cursor = connection.cursor()
        user_ids = _ensure_users(cursor)
        _seed_activity_logs(cursor, user_ids)
        connection.commit()
        cursor.close()
    finally:
        connection.close()

    _run_detection()

    connection = _get_connection()
    try:
        cursor = connection.cursor()
        _verify_alerts_and_notifications(cursor)
        cursor.close()
    finally:
        connection.close()

    print("Seed scenarios executed successfully.")


if __name__ == "__main__":
    seed()
