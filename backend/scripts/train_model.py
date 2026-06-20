"""
Train LightGBM model from historical match data.

CSV format (data/historical/matches.csv):
  home_team,away_team,home_goals,away_goals,stage,competition_type,home_strength,away_strength,days_rest
  Brazil,France,2,1,GROUP,national,1823.45,1756.20,4

Run: cd backend && python scripts/train_model.py
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
from app.ml.features import build_features
from app.ml.model import WC2026Model

DATA_PATH = "data/historical/matches.csv"


def result_label(home_goals: int, away_goals: int) -> str:
    if home_goals > away_goals:
        return "home_win"
    if home_goals == away_goals:
        return "draw"
    return "away_win"


def main():
    os.makedirs("ml_artifacts", exist_ok=True)
    df = pd.read_csv(DATA_PATH)

    for comp_type in ("national", "club_europe"):
        subset = df[df["competition_type"] == comp_type]
        if subset.empty:
            print(f"No data for {comp_type}, skipping.")
            continue

        X, y = [], []
        for _, row in subset.iterrows():
            features = build_features(
                home_team=row["home_team"],
                away_team=row["away_team"],
                competition_type=comp_type,
                home_strength=float(row["home_strength"]),
                away_strength=float(row["away_strength"]),
                home_history=[],
                away_history=[],
                h2h=[],
                stage=row.get("stage", "GROUP"),
                days_rest=int(row.get("days_rest", 4)),
            )
            X.append(features)
            y.append(result_label(int(row["home_goals"]), int(row["away_goals"])))

        model = WC2026Model()
        model.train(X, y)
        path = f"ml_artifacts/lgbm_{comp_type}.pkl"
        model.save(path)
        print(f"[{comp_type}] Trained on {len(X)} matches -> {path}")


if __name__ == "__main__":
    main()
