"""
Poisson-based score prediction.

Given expected goals (lambda) for each team, computes:
- Score probability matrix up to max_goals x max_goals
- Most likely scoreline
- Win/draw/loss probabilities (as a cross-check against LightGBM)
"""
import math
import numpy as np


def _poisson_pmf(lam: float, k: int) -> float:
    """P(X=k) for Poisson(lambda)."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def score_matrix(lambda_home: float, lambda_away: float, max_goals: int = 8) -> np.ndarray:
    """
    Returns matrix M where M[i][j] = P(home scores i, away scores j).
    Shape: (max_goals+1) x (max_goals+1)
    """
    m = np.zeros((max_goals + 1, max_goals + 1))
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            m[i][j] = _poisson_pmf(lambda_home, i) * _poisson_pmf(lambda_away, j)
    return m


def predict_score(
    lambda_home: float,
    lambda_away: float,
    max_goals: int = 8,
) -> dict:
    """
    Returns:
      - predicted_score: most likely scoreline "H-A"
      - home_win_prob, draw_prob, away_win_prob from Poisson matrix
      - score_probs: top 5 most likely scorelines with probabilities
    """
    m = score_matrix(lambda_home, lambda_away, max_goals)

    # Win/draw/loss
    home_win = float(np.sum(np.tril(m, -1)))   # i > j
    draw = float(np.sum(np.diag(m)))
    away_win = float(np.sum(np.triu(m, 1)))    # j > i

    # Most likely scoreline
    idx = np.unravel_index(np.argmax(m), m.shape)
    best_score = f"{idx[0]}-{idx[1]}"

    # Top 5 scorelines
    flat = [(m[i][j], f"{i}-{j}") for i in range(max_goals + 1) for j in range(max_goals + 1)]
    flat.sort(reverse=True)
    score_probs = [{"score": s, "prob": round(float(p) * 100, 1)} for p, s in flat[:5]]

    return {
        "predicted_score": best_score,
        "home_win_prob": home_win,
        "draw_prob": draw,
        "away_win_prob": away_win,
        "score_probs": score_probs,
    }


def estimate_lambdas(features: dict) -> tuple[float, float]:
    """
    Estimate expected goals from feature dict.
    Blends DB history-based estimate with Elo-based baseline.
    """
    home_att = features.get("home_goals_scored_avg", 1.3)
    home_def = features.get("home_goals_conceded_avg", 1.1)
    away_att = features.get("away_goals_scored_avg", 1.1)
    away_def = features.get("away_goals_conceded_avg", 1.3)
    home_adv = features.get("home_advantage", 0.0)
    elo_prob = features.get("elo_home_win_prob", 0.5)

    # Elo-based lambda baseline
    # WC modern avg ~2.7 goals/game → 1.35 each at equal strength
    # Linear scale: at 50% → 1.35 each; at 80% → home ~2.2, away ~0.7
    wc_per_team = 1.35
    spread = 2.8  # how much goals shift with win prob
    elo_lambda_home = wc_per_team + (elo_prob - 0.5) * spread
    elo_lambda_away = wc_per_team + ((1 - elo_prob) - 0.5) * spread
    elo_lambda_home = max(0.4, elo_lambda_home)
    elo_lambda_away = max(0.4, elo_lambda_away)

    # History-based lambda
    league_avg = 1.3
    hist_lambda_home = (home_att / league_avg) * (away_def / league_avg) * league_avg
    hist_lambda_away = (away_att / league_avg) * (home_def / league_avg) * league_avg

    # Blend history only when team has played ≥3 matches (h2h_count proxy via win/draw rates)
    # Use home_goals_scored_avg10 vs default to detect if we have real data
    home_games10 = features.get("home_goals_scored_avg10", 1.0)
    away_games10 = features.get("away_goals_scored_avg10", 1.0)
    has_home_history = home_att != 1.0 and home_games10 != 1.0
    has_away_history = away_att != 1.0 and away_games10 != 1.0

    if has_home_history and has_away_history:
        hist_weight = 0.5
    elif has_home_history or has_away_history:
        hist_weight = 0.25
    else:
        hist_weight = 0.0
    elo_weight = 1.0 - hist_weight

    lambda_home = elo_weight * elo_lambda_home + hist_weight * hist_lambda_home
    lambda_away = elo_weight * elo_lambda_away + hist_weight * hist_lambda_away

    # Home advantage boost (neutral = 0)
    lambda_home *= (1 + home_adv)

    lambda_home = max(0.4, min(lambda_home, 5.0))
    lambda_away = max(0.4, min(lambda_away, 5.0))

    return lambda_home, lambda_away
