from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    SECRET_KEY = os.getenv("SECRET_KEY", "cybersentinel-secret")
    SESSION_COOKIE_NAME = os.getenv("SESSION_COOKIE_NAME", "cybersentinel_session")

    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    MYSQL_DB = os.getenv("MYSQL_DB", "cyber_sentinel_db")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", 3306))
    MYSQL_POOL_SIZE = int(os.getenv("MYSQL_POOL_SIZE", 5))

    HF_API_BASE = os.getenv("HF_API_BASE")
    HF_API_KEY = os.getenv("HF_API_KEY")

    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def mysql_config(cls) -> dict:
        """Return a mysql.connector configuration dictionary."""
        return {
            "host": cls.MYSQL_HOST,
            "user": cls.MYSQL_USER,
            "password": cls.MYSQL_PASSWORD,
            "database": cls.MYSQL_DB,
            "port": cls.MYSQL_PORT,
            "auth_plugin": os.getenv("MYSQL_AUTH_PLUGIN", "mysql_native_password"),
        }
