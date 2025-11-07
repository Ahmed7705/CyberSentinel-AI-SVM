from __future__ import annotations

from datetime import datetime, timedelta
import os

from database.database import fetch_all
from tests import _reporter as reporter

from ai_engine.engine import AIEngine, RISK_HIGH_THRESHOLD


def _scenario_timestamp(hour: int) -> datetime:
    today = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    return today - timedelta(days=1, hours=today.hour - hour)


def test_ai_training_and_detection(flask_app):
    with flask_app.app_context():
        engine: AIEngine = flask_app.extensions["ai_engine"]
        engine.warm_start()
        reporter.mark_ok("AI training")

        late_night = {
            "user_id": 3,
            "event_type": "late_night_login",
            "timestamp": _scenario_timestamp(3),
            "source_ip": "10.0.2.18",
            "device": "Surface-Pro-HR03",
            "location": "Remote",
            "failed_attempts": 0,
            "description": "Login detected at 03:00",
        }
        mass_copy = {
            "user_id": 9,
            "event_type": "mass_copy",
            "timestamp": datetime.utcnow(),
            "source_ip": "10.0.4.77",
            "device": "MacBook-Pro-PD01",
            "bytes_transferred": int(1.7 * 1024 * 1024 * 1024),
            "files_accessed": 140,
            "description": "Massive data copy operation",
        }
        remote_script = {
            "user_id": 6,
            "event_type": "remote_download",
            "timestamp": datetime.utcnow(),
            "source_ip": "203.0.113.88",
            "device": "Automation-VM",
            "user_agent": "Python-urllib/3.13",
            "description": "Remote script download via Python",
        }

        results = [engine.analyse_activity(payload) for payload in (late_night, mass_copy, remote_script)]
        for result in results:
            assert result.risk_score >= RISK_HIGH_THRESHOLD or result.risk_level in {"high", "critical"}

        alerts = fetch_all("SELECT risk_level FROM alerts ORDER BY id DESC LIMIT 3")
        assert alerts, "Expected alerts to be recorded"
        reporter.mark_ok("AI detection (late-night, mass-copy, remote-script)")

        if os.getenv("HF_API_KEY"):
            insight = results[0].insight or ""
            assert insight.strip()
