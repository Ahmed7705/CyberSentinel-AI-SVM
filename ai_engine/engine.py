"""Core AI engine orchestrating anomaly detection."""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Dict

from openai import OpenAI

from ai_engine.data_preprocessor import DataPreprocessor
from ai_engine.isolation_forest import IsolationForestModel
from ai_engine.one_class_svm import OneClassSVMModel
from database.database import fetch_all
from services import alert_service

logger = logging.getLogger(__name__)

RISK_MEDIUM_THRESHOLD = 0.4
RISK_HIGH_THRESHOLD = 0.7
RISK_CRITICAL_THRESHOLD = 0.9


ARABIC_CHAR_PATTERN = re.compile(r"[\u0600-\u06FF]")


def _is_arabic_prompt(message: str) -> bool:
    return bool(ARABIC_CHAR_PATTERN.search(message))


def generate_alert_insight(alert_message: str) -> str | None:
    """Generate an LLM-based insight for the supplied alert."""
    api_key = os.getenv("HF_API_KEY")
    if not api_key:
        logger.debug("HF_API_KEY not configured; skipping LLM insight generation")
        return None

    client = OpenAI(
        base_url=os.getenv("HF_API_BASE", "https://router.huggingface.co/v1"),
        api_key=api_key,
    )
    try:
        use_arabic = _is_arabic_prompt(alert_message)
        response_language = "Modern Standard Arabic" if use_arabic else "English"
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-7B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an AI cyber security analyst. Respond in "
                        f"{response_language} matching the user's request. Provide concise, well-structured "
                        "answers with short headings and up to five bullet points, then end with one actionable "
                        "recommendation. Keep the overall response under roughly 130 words."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Prompt language preference: {response_language}. "
                        "Deliver a tidy and concise cyber security insight for this request:\n"
                        f"{alert_message}\n"
                        "Ensure the answer remains complete while staying brief."
                    ),
                },
            ],
            max_tokens=280,
        )
    except Exception as exc:  # pragma: no cover - defensive guard against remote API failures
        logger.warning("Insight generation failed: %s", exc)
        return None
    return response.choices[0].message.content


@dataclass(slots=True)
class DetectionResult:
    risk_score: float
    risk_level: str
    iso_score: float
    svm_score: float
    anomaly_votes: int
    insight: str | None

    def as_dict(self) -> Dict[str, Any]:
        return {
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "iso_score": self.iso_score,
            "svm_score": self.svm_score,
            "anomaly_votes": self.anomaly_votes,
            "insight": self.insight,
        }


class AIEngine:
    """Coordinates preprocessing, ML models, and alert persistence."""

    def __init__(self) -> None:
        self.preprocessor = DataPreprocessor()
        self.isolation_forest = IsolationForestModel()
        self.one_class_svm = OneClassSVMModel()
        self.is_trained = False

    def warm_start(self, limit: int = 500) -> None:
        """Train the models from historical activity data when available."""
        try:
            logs = fetch_all(
                """
                SELECT user_id, event_type, source_ip, device, location, bytes_transferred,
                       files_accessed, failed_attempts, session_duration, timestamp
                FROM activity_logs
                ORDER BY timestamp DESC
                LIMIT %s
                """,
                (limit,),
            )
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.warning("Unable to load baseline activity logs: %s", exc)
            return

        if not logs:
            logger.info("No historical activity logs available to warm start models")
            return

        features = self.preprocessor.fit(logs)
        self.isolation_forest.fit(features)
        self.one_class_svm.fit(features)
        self.is_trained = True
        logger.info("AI models trained with %s baseline events", len(logs))

    def ensure_trained(self) -> None:
        if self.is_trained:
            return
        # Attempt a minimal warm start if not already done.
        self.warm_start(limit=200)
        if not self.is_trained:
            raise RuntimeError("AIEngine models have not been trained; add activity logs first")

    def analyse_activity(self, activity: dict, persist: bool = True) -> DetectionResult:
        self.ensure_trained()
        features = self.preprocessor.transform(activity)
        iso_score = self.isolation_forest.score(features)
        svm_score = self.one_class_svm.score(features)
        anomaly_votes = self.isolation_forest.predict(features) + self.one_class_svm.predict(features)

        # Convert combined scores into a 0..1 risk score. Lower scores indicate anomalies.
        combined = -(iso_score + svm_score) / 2.0
        risk_score = max(0.0, min(1.0, 0.5 + combined))
        heuristic_score = self._heuristic_score(activity)
        if heuristic_score is not None:
            risk_score = max(risk_score, heuristic_score)

        risk_level = self._determine_risk_level(risk_score, anomaly_votes)
        insight = None

        if risk_level in {"high", "critical"}:
            try:
                insight = generate_alert_insight(activity.get("description", "Potential insider threat"))
            except Exception as exc:  # pragma: no cover - network errors are non-fatal
                logger.warning("Insight generation failed: %s", exc)

        if persist and risk_level in {"medium", "high", "critical"}:
            self._persist_alert(activity, risk_score, risk_level, insight)

        return DetectionResult(risk_score, risk_level, iso_score, svm_score, anomaly_votes, insight)

    def _persist_alert(self, activity: dict, risk_score: float, risk_level: str, insight: str | None) -> None:
        metadata = json.dumps(activity, default=str)
        description = activity.get("description") or activity.get("event_type") or "Suspicious activity detected"
        user_id = activity.get("user_id")
        alert_service.create_alert(user_id, "Insider Threat", description, risk_score, risk_level, metadata)
        if insight:
            alert_service.create_alert(user_id, "LLM Insight", insight, min(risk_score + 0.1, 1.0), risk_level, metadata)

    def _coerce_datetime(self, value: Any) -> datetime | None:
        if isinstance(value, datetime):
            return value
        if not value:
            return None
        try:
            return datetime.fromisoformat(str(value))
        except ValueError:
            try:
                return datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None

    def _heuristic_score(self, activity: dict) -> float | None:
        """Blend deterministic signals with ML output for predictable scoring."""
        score = 0.0
        event_type = (activity.get("event_type") or "").lower()
        description = (activity.get("description") or "").lower()
        bytes_transferred = float(activity.get("bytes_transferred") or 0)
        files_accessed = int(activity.get("files_accessed") or 0)
        failed_attempts = int(activity.get("failed_attempts") or 0)
        timestamp = self._coerce_datetime(activity.get("timestamp"))
        hour = timestamp.hour if timestamp else None

        if hour is not None and (hour < 4 or hour > 22):
            score = max(score, 0.72)

        if "mass" in event_type or "copy" in event_type or files_accessed >= 100:
            score = max(score, 0.78)
        if bytes_transferred >= 1.5 * 1024 * 1024 * 1024 or "download" in event_type:
            score = max(score, 0.8)

        user_agent = (activity.get("user_agent") or "").lower()
        source_ip = (activity.get("source_ip") or "0.0.0.0")
        if "python" in user_agent or "urllib" in user_agent or source_ip.startswith("198.51.") or source_ip.startswith("203.0.113."):
            score = max(score, 0.75)

        if failed_attempts >= 3:
            score = max(score, 0.65)

        if "privilege" in description:
            score = max(score, 0.76)

        if score == 0.0:
            return None
        return min(1.0, score)

    @staticmethod
    def _determine_risk_level(risk_score: float, votes: int) -> str:
        if risk_score >= RISK_CRITICAL_THRESHOLD or votes >= 2:
            return "critical"
        if risk_score >= RISK_HIGH_THRESHOLD:
            return "high"
        if risk_score >= RISK_MEDIUM_THRESHOLD:
            return "medium"
        return "low"
