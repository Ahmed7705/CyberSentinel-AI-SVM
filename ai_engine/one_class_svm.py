"""One-Class SVM wrapper."""
from __future__ import annotations

from sklearn.svm import OneClassSVM


class OneClassSVMModel:
    def __init__(self, kernel: str = "rbf", gamma: str | float = "scale", nu: float = 0.1) -> None:
        self.model = OneClassSVM(kernel=kernel, gamma=gamma, nu=nu)
        self.is_trained = False

    def fit(self, features) -> None:
        self.model.fit(features)
        self.is_trained = True

    def score(self, features) -> float:
        if not self.is_trained:
            raise RuntimeError("OneClassSVMModel must be trained before scoring")
        decision = self.model.decision_function(features)
        return float(decision.mean())

    def predict(self, features) -> int:
        if not self.is_trained:
            raise RuntimeError("OneClassSVMModel must be trained before prediction")
        prediction = self.model.predict(features)
        return int(prediction[0] == -1)
