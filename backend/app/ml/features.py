KNOCKOUT_STAGES = {"ROUND_OF_16", "QUARTER_FINAL", "SEMI_FINAL", "FINAL", "THIRD_PLACE"}


def _form_points(history: list) -> float:
    points = {"W": 3, "D": 1, "L": 0}
    recent = history[-5:] if len(history) >= 5 else history
    if not recent:
        return 1.5
    return sum(points[m["result"]] for m in recent) / len(recent)


def _avg(history: list, key: str) -> float:
    recent = history[-5:] if len(history) >= 5 else history
    if not recent:
        return 1.0
    return sum(m[key] for m in recent) / len(recent)


def _h2h_home_win_rate(h2h: list) -> float:
    if not h2h:
        return 0.5
    wins = sum(1 for m in h2h if m["home_goals"] > m["away_goals"])
    return wins / len(h2h)


def _h2h_avg_goals(h2h: list) -> float:
    if not h2h:
        return 2.5
    return sum(m["home_goals"] + m["away_goals"] for m in h2h) / len(h2h)


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
) -> dict:
    home_advantage = 0.1 if competition_type == "national" else 0.35

    return {
        "home_strength": home_strength,
        "away_strength": away_strength,
        "strength_diff": home_strength - away_strength,
        "home_advantage": home_advantage,
        "home_form_points": _form_points(home_history),
        "away_form_points": _form_points(away_history),
        "home_goals_scored_avg": _avg(home_history, "goals_scored"),
        "home_goals_conceded_avg": _avg(home_history, "goals_conceded"),
        "away_goals_scored_avg": _avg(away_history, "goals_scored"),
        "away_goals_conceded_avg": _avg(away_history, "goals_conceded"),
        "h2h_home_win_rate": _h2h_home_win_rate(h2h),
        "h2h_avg_goals": _h2h_avg_goals(h2h),
        "is_knockout": 1 if stage.upper() in KNOCKOUT_STAGES else 0,
        "days_rest": days_rest,
    }
