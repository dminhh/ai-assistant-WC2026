import pytest
import os
from app.ml.model import WC2026Model

FEATURE_KEYS = [
    "home_strength", "away_strength", "strength_diff", "home_advantage",
    "home_form_points", "away_form_points",
    "home_goals_scored_avg", "home_goals_conceded_avg",
    "away_goals_scored_avg", "away_goals_conceded_avg",
    "h2h_home_win_rate", "h2h_avg_goals", "is_knockout", "days_rest",
]


def _make_features(strength_diff=100.0):
    return {k: 1.5 for k in FEATURE_KEYS} | {"strength_diff": strength_diff, "is_knockout": 0, "days_rest": 4}


def _training_data(n=120):
    X = [_make_features(float(i % 300 - 150)) for i in range(n)]
    y = ["home_win" if i % 3 == 0 else "draw" if i % 3 == 1 else "away_win" for i in range(n)]
    return X, y


def test_predict_sums_to_one():
    model = WC2026Model()
    X, y = _training_data()
    model.train(X, y)
    result = model.predict(_make_features())
    total = result["home_win"] + result["draw"] + result["away_win"]
    assert abs(total - 1.0) < 1e-6


def test_predict_all_probs_in_range():
    model = WC2026Model()
    X, y = _training_data()
    model.train(X, y)
    result = model.predict(_make_features())
    for k in ("home_win", "draw", "away_win"):
        assert 0.0 <= result[k] <= 1.0


def test_confidence_is_valid():
    model = WC2026Model()
    X, y = _training_data()
    model.train(X, y)
    result = model.predict(_make_features())
    assert result["confidence"] in ("low", "medium", "high")


def test_save_load_roundtrip(tmp_path):
    model = WC2026Model()
    X, y = _training_data()
    model.train(X, y)
    path = str(tmp_path / "model.pkl")
    model.save(path)
    loaded = WC2026Model.load(path)
    r1 = model.predict(_make_features())
    r2 = loaded.predict(_make_features())
    assert abs(r1["home_win"] - r2["home_win"]) < 1e-6
