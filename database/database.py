"""Database helpers for CyberSentinel AI."""
from __future__ import annotations

import logging
from contextlib import contextmanager

import mysql.connector
from flask import current_app
from mysql.connector.pooling import MySQLConnectionPool

logger = logging.getLogger(__name__)
_connection_pool: MySQLConnectionPool | None = None


def init_app(app) -> None:
    """Initialise the database helpers for the given Flask app."""
    configure_logging(app)
    app.teardown_appcontext(close_db_connection)


def configure_logging(app) -> None:
    level = getattr(logging, app.config.get("LOG_LEVEL", "INFO").upper(), logging.INFO)
    logger.setLevel(level)


def _get_pool() -> MySQLConnectionPool:
    global _connection_pool
    if _connection_pool is None:
        cfg = current_app.config
        pool_config = {
            "pool_name": "cybersentinel_pool",
            "pool_size": cfg.get("MYSQL_POOL_SIZE", 5),
            "host": cfg.get("MYSQL_HOST"),
            "user": cfg.get("MYSQL_USER"),
            "password": cfg.get("MYSQL_PASSWORD"),
            "database": cfg.get("MYSQL_DB"),
            "port": cfg.get("MYSQL_PORT", 3306),
            "auth_plugin": cfg.get("MYSQL_AUTH_PLUGIN", "mysql_native_password"),
            "raise_on_warnings": True,
            "autocommit": False,
            "pool_reset_session": True,
        }
        _connection_pool = MySQLConnectionPool(**pool_config)
    return _connection_pool


def get_db_connection():
    """Get a connection for the current request context."""
    pool = _get_pool()
    return pool.get_connection()


def close_db_connection(_: Exception | None = None) -> None:
    """Compatibility hook; connections are returned to the pool per query."""
    return None


@contextmanager
def get_cursor(dictionary: bool = True):
    """Context manager that yields a cursor and handles commit/rollback."""
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=dictionary)
    try:
        yield cursor
        connection.commit()
    except mysql.connector.Error as exc:  # pragma: no cover - defensive logging
        connection.rollback()
        logger.exception("Database error: %s", exc)
        raise
    finally:
        cursor.close()
        connection.close()


def fetch_one(query: str, params: tuple | dict | None = None):
    with get_cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchone()


def fetch_all(query: str, params: tuple | dict | None = None):
    with get_cursor() as cur:
        cur.execute(query, params or ())
        return cur.fetchall()


def execute(query: str, params: tuple | dict | None = None) -> int:
    with get_cursor() as cur:
        cur.execute(query, params or ())
        return cur.rowcount
