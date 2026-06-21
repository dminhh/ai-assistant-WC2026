"""
Train LightGBM model for national team match prediction.
Uses international football results from 2010 onwards (Kaggle dataset).

Run: cd backend && python scripts/train_model.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import numpy as np
from collections import defaultdict

from app.ml.features import build_features
from app.ml.model import WC2026Model, FEATURE_ORDER

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "international_results.csv")
OUTPUT_PATH = "ml_artifacts/lgbm_national.pkl"

KNOCKOUT_KEYWORDS = {"round of 16", "quarter-final", "semi-final", "final", "third place"}


def get_stage(tournament: str) -> str:
    t = tournament.lower()
    for kw in KNOCKOUT_KEYWORDS:
        if kw in t:
            return "ROUND_OF_16"
    return "GROUP"


def compute_elo(df: pd.DataFrame, k: int = 32, initial: float = 1500.0) -> dict:
    ratings: dict = defaultdict(lambda: initial)
    for _, row in df.iterrows():
        if pd.isna(row["home_score"]) or pd.isna(row["away_score"]):
            continue
        h, a = row["home_team"], row["away_team"]
        rh, ra = ratings[h], ratings[a]
        expected_h = 1 / (1 + 10 ** ((ra - rh) / 400))
        hs, as_ = int(row["home_score"]), int(row["away_score"])
        if hs > as_:
            score_h = 1.0
        elif hs == as_:
            score_h = 0.5
        else:
            score_h = 0.0
        ratings[h] += k * (score_h - expected_h)
        ratings[a] += k * ((1 - score_h) - (1 - expected_h))
    return dict(ratings)


def build_h2h_map(df: pd.DataFrame) -> dict:
    h2h: dict = defaultdict(list)
    for _, row in df.iterrows():
        if pd.isna(row["home_score"]) or pd.isna(row["away_score"]):
            continue
        key = tuple(sorted([row["home_team"], row["away_team"]]))
        h2h[key].append({
            "home_goals": int(row["home_score"]),
            "away_goals": int(row["away_score"]),
            "home_team": row["home_team"],
        })
    return dict(h2h)


def main():
    os.makedirs("ml_artifacts", exist_ok=True)

    print("Loading data...")
    df_all = pd.read_csv(DATA_PATH, parse_dates=["date"])
    df_all = df_all.sort_values("date").reset_index(drop=True)

    # Compute Elo on full history for better initial ratings
    print("Computing Elo ratings from full history...")
    elo = compute_elo(df_all)

    # Filter 2010+ with known scores
    df = df_all[df_all["date"] >= "2010-01-01"].copy()
    df = df.dropna(subset=["home_score", "away_score"]).reset_index(drop=True)
    print(f"Training on {len(df)} matches from 2010+")

    h2h_map = build_h2h_map(df)
    team_history: dict = defaultdict(list)

    X, y = [], []
    for _, row in df.iterrows():
        h, a = row["home_team"], row["away_team"]
        hs, as_ = int(row["home_score"]), int(row["away_score"])

        h_hist = team_history[h][-10:]
        a_hist = team_history[a][-10:]

        key = tuple(sorted([h, a]))
        raw_h2h = h2h_map.get(key, [])[-5:]
        h2h_adj = []
        for m in raw_h2h:
            if m["home_team"] == h:
                h2h_adj.append({"home_goals": m["home_goals"], "away_goals": m["away_goals"]})
            else:
                h2h_adj.append({"home_goals": m["away_goals"], "away_goals": m["home_goals"]})

        feats = build_features(
            home_team=h, away_team=a,
            competition_type="national",
            home_strength=elo.get(h, 1500.0),
            away_strength=elo.get(a, 1500.0),
            home_history=h_hist, away_history=a_hist,
            h2h=h2h_adj,
            stage=get_stage(row["tournament"]),
            days_rest=4,
            is_neutral=bool(row.get("neutral", False)),
            tournament=str(row.get("tournament", "")),
        )
        X.append(feats)

        if hs > as_:
            label = "home_win"
            hr, ar = "W", "L"
        elif hs == as_:
            label = "draw"
            hr = ar = "D"
        else:
            label = "away_win"
            hr, ar = "L", "W"
        y.append(label)

        team_history[h].append({"result": hr, "goals_scored": hs, "goals_conceded": as_})
        team_history[a].append({"result": ar, "goals_scored": as_, "goals_conceded": hs})

    print(f"Label distribution: {pd.Series(y).value_counts().to_dict()}")

    print("Training LightGBM model...")
    model = WC2026Model()
    model.train(X, y)
    model.save(OUTPUT_PATH)
    print(f"Model saved to {OUTPUT_PATH}")

    # Quick accuracy on last 1000 matches
    X_eval = np.array([[row[k] for k in FEATURE_ORDER] for row in X[-1000:]])
    y_eval = y[-1000:]
    preds_raw = model._model.predict(X_eval)
    preds = [model._encoder.classes_[np.argmax(p)] for p in preds_raw]
    acc = sum(p == t for p, t in zip(preds, y_eval)) / len(y_eval)
    print(f"Accuracy on last 1000 matches: {acc:.1%}")


if __name__ == "__main__":
    main()
