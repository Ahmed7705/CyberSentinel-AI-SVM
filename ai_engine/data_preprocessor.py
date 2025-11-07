"""Utilities for converting raw activity logs into ML-ready features."""
from __future__ import annotations

import pandas as pd

NUMERICAL_FIELDS = ["bytes_transferred", "files_accessed", "failed_attempts", "session_duration"]
CATEGORICAL_FIELDS = ["event_type", "source_ip", "device", "location"]


class DataPreprocessor:
    def __init__(self) -> None:
        self.fitted_columns: list[str] | None = None

    def fit(self, logs: list[dict]) -> pd.DataFrame:
        frame = self._to_frame(logs)
        encoded = self._encode(frame)
        self.fitted_columns = encoded.columns.tolist()
        return encoded

    def transform(self, log: dict | list[dict]) -> pd.DataFrame:
        logs = log if isinstance(log, list) else [log]
        frame = self._to_frame(logs)
        encoded = self._encode(frame)
        if self.fitted_columns is None:
            self.fitted_columns = encoded.columns.tolist()
        else:
            for column in self.fitted_columns:
                if column not in encoded.columns:
                    encoded[column] = 0
            encoded = encoded[self.fitted_columns]
        return encoded

    def _to_frame(self, logs: list[dict]) -> pd.DataFrame:
        frame = pd.DataFrame(logs)
        if "timestamp" in frame.columns:
            frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
            frame["hour"] = frame["timestamp"].dt.hour.fillna(0)
            frame["day_of_week"] = frame["timestamp"].dt.dayofweek.fillna(0)
        else:
            frame["hour"] = 0
            frame["day_of_week"] = 0
        for field in NUMERICAL_FIELDS:
            if field not in frame:
                frame[field] = 0
            frame[field] = pd.to_numeric(frame[field], errors="coerce").fillna(0)
        for field in CATEGORICAL_FIELDS:
            if field not in frame:
                frame[field] = "unknown"
            frame[field] = frame[field].fillna("unknown")
        return frame

    def _encode(self, frame: pd.DataFrame) -> pd.DataFrame:
        categorical = pd.get_dummies(frame[CATEGORICAL_FIELDS], prefix=CATEGORICAL_FIELDS, dtype=int)
        numerical = frame[["hour", "day_of_week"] + NUMERICAL_FIELDS]
        numerical = numerical.astype(float)
        return pd.concat([numerical, categorical], axis=1)
