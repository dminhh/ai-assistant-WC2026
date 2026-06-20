from __future__ import annotations
import joblib
import numpy as np
import lightgbm as lgb
from sklearn.preprocessing import LabelEncoder

FEATURE_ORDER = [
    "home_strength", "away_strength", "strength_diff", "home_advantage",
    "home_form_points", "away_form_points",
    "home_goals_scored_avg", "home_goals_conceded_avg",
    "away_goals_scored_avg", "away_goals_conceded_avg",
    "h2h_home_win_rate", "h2h_avg_goals", "is_knockout", "days_rest",
]


def _confidence(probs: list[float]) -> str:
    m = max(probs)
    if m > 0.60:
        return "high"
    if m >= 0.45:
        return "medium"
    return "low"


class WC2026Model:
    def __init__(self):
        self._model: lgb.Booster | None = None
        self._encoder = LabelEncoder()

    def _to_matrix(self, X: list[dict]) -> np.ndarray:
        return np.array([[row[k] for k in FEATURE_ORDER] for row in X])

    def train(self, X: list[dict], y: list[str]) -> None:
        X_mat = self._to_matrix(X)
        y_enc = self._encoder.fit_transform(y)
        params = {
            "objective": "multiclass",
            "num_class": 3,
            "metric": "multi_logloss",
            "num_leaves": 31,
            "learning_rate": 0.05,
            "verbose": -1,
        }
        train_data = lgb.Dataset(X_mat, label=y_enc)
        self._model = lgb.train(params, train_data, num_boost_round=300)

    def predict(self, features: dict) -> dict:
        if self._model is None:
            raise RuntimeError("Model not trained.")
        X_mat = self._to_matrix([features])
        probs = self._model.predict(X_mat)[0]
        classes = list(self._encoder.classes_)
        prob_map = dict(zip(classes, probs.tolist()))
        return {
            "home_win": prob_map.get("home_win", 0.33),
            "draw": prob_map.get("draw", 0.33),
            "away_win": prob_map.get("away_win", 0.34),
            "confidence": _confidence(probs.tolist()),
        }

    def save(self, path: str) -> None:
        joblib.dump({"model": self._model, "encoder": self._encoder}, path)

    @classmethod
    def load(cls, path: str) -> "WC2026Model":
        inst = cls()
        data = joblib.load(path)
        inst._model = data["model"]
        inst._encoder = data["encoder"]
        return inst
