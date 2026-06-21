import math

KNOCKOUT_STAGES = {"ROUND_OF_16", "QUARTER_FINAL", "SEMI_FINAL", "FINAL", "THIRD_PLACE"}

TOURNAMENT_WEIGHT = {
    "fifa world cup": 1.0,
    "world cup": 1.0,
    "uefa euro": 0.95,
    "copa america": 0.95,
    "africa cup of nations": 0.90,
    "asian cup": 0.85,
    "concacaf gold cup": 0.80,
    "qualification": 0.75,
    "friendly": 0.40,
}


def _tournament_weight(tournament: str) -> float:
    t = tournament.lower()
    for key, w in TOURNAMENT_WEIGHT.items():
        if key in t:
            return w
    return 0.70


def _form_points_weighted(history: list, n: int = 10) -> float:
    """Exponentially weighted form — recent matches matter more."""
    points = {"W": 3, "D": 1, "L": 0}
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 1.5
    decay = 0.85
    weights = [decay ** (len(recent) - 1 - i) for i in range(len(recent))]
    total_w = sum(weights)
    return sum(weights[i] * points[recent[i]["result"]] for i in range(len(recent))) / total_w


def _avg(history: list, key: str, n: int = 5) -> float:
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 1.0
    return sum(m[key] for m in recent) / len(recent)


def _win_rate(history: list, n: int = 10) -> float:
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 0.33
    return sum(1 for m in recent if m["result"] == "W") / len(recent)


def _draw_rate(history: list, n: int = 10) -> float:
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 0.25
    return sum(1 for m in recent if m["result"] == "D") / len(recent)


def _clean_sheet_rate(history: list, n: int = 5) -> float:
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 0.2
    return sum(1 for m in recent if m["goals_conceded"] == 0) / len(recent)


def _scoring_rate(history: list, n: int = 5) -> float:
    recent = history[-n:] if len(history) >= n else history
    if not recent:
        return 0.8
    return sum(1 for m in recent if m["goals_scored"] > 0) / len(recent)


def _h2h_home_win_rate(h2h: list) -> float:
    if not h2h:
        return 0.45
    wins = sum(1 for m in h2h if m["home_goals"] > m["away_goals"])
    return wins / len(h2h)


def _h2h_avg_goals(h2h: list) -> float:
    if not h2h:
        return 2.5
    return sum(m["home_goals"] + m["away_goals"] for m in h2h) / len(h2h)


def _h2h_draw_rate(h2h: list) -> float:
    if not h2h:
        return 0.25
    return sum(1 for m in h2h if m["home_goals"] == m["away_goals"]) / len(h2h)


def _elo_win_prob(elo_h: float, elo_a: float) -> float:
    return 1 / (1 + 10 ** ((elo_a - elo_h) / 400))


def build_features(
    home_team: str,
    away_team: str,
    competition_type: str,
    home_strength: float,
    away_strength: float,
    home_history: list,
    away_history: list,
    h2h: list,
    stage: str,
    days_rest: int = 4,
    is_neutral: bool = False,
    tournament: str = "",
) -> dict:
    home_advantage = 0.0 if is_neutral else (0.08 if competition_type == "national" else 0.30)
    elo_diff = home_strength - away_strength
    elo_home_win_prob = _elo_win_prob(home_strength, away_strength)

    return {
        # Elo features
        "home_strength": home_strength,
        "away_strength": away_strength,
        "strength_diff": elo_diff,
        "elo_home_win_prob": elo_home_win_prob,
        "elo_ratio": home_strength / max(away_strength, 1),

        # Home advantage
        "home_advantage": home_advantage,
        "is_neutral": 1 if is_neutral else 0,

        # Form (weighted, last 10)
        "home_form_points": _form_points_weighted(home_history, 10),
        "away_form_points": _form_points_weighted(away_history, 10),
        "form_diff": _form_points_weighted(home_history, 10) - _form_points_weighted(away_history, 10),

        # Win/draw rates
        "home_win_rate": _win_rate(home_history, 10),
        "away_win_rate": _win_rate(away_history, 10),
        "home_draw_rate": _draw_rate(home_history, 10),
        "away_draw_rate": _draw_rate(away_history, 10),

        # Goals (last 5)
        "home_goals_scored_avg": _avg(home_history, "goals_scored", 5),
        "home_goals_conceded_avg": _avg(home_history, "goals_conceded", 5),
        "away_goals_scored_avg": _avg(away_history, "goals_scored", 5),
        "away_goals_conceded_avg": _avg(away_history, "goals_conceded", 5),

        # Goals (last 10)
        "home_goals_scored_avg10": _avg(home_history, "goals_scored", 10),
        "away_goals_scored_avg10": _avg(away_history, "goals_scored", 10),

        # Defense
        "home_clean_sheet_rate": _clean_sheet_rate(home_history, 5),
        "away_clean_sheet_rate": _clean_sheet_rate(away_history, 5),
        "home_scoring_rate": _scoring_rate(home_history, 5),
        "away_scoring_rate": _scoring_rate(away_history, 5),

        # Attack vs defense matchup
        "home_attack_vs_away_defense": _avg(home_history, "goals_scored", 5) - _avg(away_history, "goals_conceded", 5),
        "away_attack_vs_home_defense": _avg(away_history, "goals_scored", 5) - _avg(home_history, "goals_conceded", 5),

        # H2H
        "h2h_home_win_rate": _h2h_home_win_rate(h2h),
        "h2h_avg_goals": _h2h_avg_goals(h2h),
        "h2h_draw_rate": _h2h_draw_rate(h2h),
        "h2h_count": min(len(h2h), 10),

        # Match context
        "is_knockout": 1 if stage.upper() in KNOCKOUT_STAGES else 0,
        "days_rest": min(days_rest, 14),
        "tournament_weight": _tournament_weight(tournament),
    }
