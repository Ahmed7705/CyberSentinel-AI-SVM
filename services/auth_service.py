"""Authentication service handling user lifecycle."""
from __future__ import annotations

import bcrypt
from datetime import datetime
from typing import Optional

from database.database import execute, fetch_all, fetch_one


def hash_password(plaintext: str) -> str:
    return bcrypt.hashpw(plaintext.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plaintext: str, hashed: str) -> bool:
    if not hashed:
        return False
    return bcrypt.checkpw(plaintext.encode("utf-8"), hashed.encode("utf-8"))


def get_user_by_username(username: str) -> Optional[dict]:
    return fetch_one("SELECT * FROM users WHERE username = %s", (username,))


def get_user_by_id(user_id: int) -> Optional[dict]:
    return fetch_one("SELECT * FROM users WHERE id = %s", (user_id,))


def list_users(limit: int | None = None) -> list[dict]:
    query = "SELECT id, username, full_name, role, department, last_login FROM users ORDER BY created_at DESC"
    if limit:
        query += " LIMIT %s"
        return fetch_all(query, (limit,))
    return fetch_all(query)


def register_user(username: str, password: str, full_name: str, role: str, department: str = "Unknown") -> int:
    hashed = hash_password(password)
    return execute(
        """
        INSERT INTO users (username, password_hash, full_name, role, department, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (username, hashed, full_name, role, department, datetime.utcnow()),
    )


def authenticate_user(username: str, password: str) -> Optional[dict]:
    user = get_user_by_username(username)
    if user and verify_password(password, user.get("password_hash", "")):
        execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.utcnow(), user["id"]))
        record_audit_event(user["id"], "login_success", f"User {username} logged in successfully")
        return user
    record_audit_event(None, "login_failed", f"Failed login attempt for username {username}")
    return None


def record_audit_event(user_id: Optional[int], event_type: str, message: str) -> None:
    execute(
        """
        INSERT INTO audit_logs (user_id, event_type, message, created_at)
        VALUES (%s, %s, %s, %s)
        """,
        (user_id, event_type, message, datetime.utcnow()),
    )


def deactivate_user(user_id: int) -> int:
    return execute("UPDATE users SET is_active = 0 WHERE id = %s", (user_id,))
