"""Isolation Forest wrapper."""
from __future__ import annotations

from sklearn.ensemble import IsolationForest


class IsolationForestModel:
    def __init__(self, contamination: float = 0.05, random_state: int = 42) -> None:
        self.model = IsolationForest(contamination=contamination, random_state=random_state)
        self.is_trained = False

    def fit(self, features) -> None:
        self.model.fit(features)
        self.is_trained = True

    def score(self, features) -> float:
        if not self.is_trained:
            raise RuntimeError("IsolationForestModel must be trained before scoring")
        decision = self.model.decision_function(features)
        return float(decision.mean())

    def predict(self, features) -> int:
        if not self.is_trained:
            raise RuntimeError("IsolationForestModel must be trained before prediction")
        # Returns 1 for normal, -1 for anomaly. Convert to 0/1 anomaly flag.
        prediction = self.model.predict(features)
        return int(prediction[0] == -1)
