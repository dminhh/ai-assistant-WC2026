import pytest
from app.ml.features import build_features


def _history(wins=3, draws=1, losses=1, goals_scored=2.0, goals_conceded=1.0):
    results = ["W"] * wins + ["D"] * draws + ["L"] * losses
    return [
        {"result": r, "goals_scored": goals_scored, "goals_conceded": goals_conceded}
        for r in results
    ]


def _h2h(home_wins=3, draws=1, away_wins=1):
    rows = []
    rows += [{"home_goals": 2, "away_goals": 0}] * home_wins
    rows += [{"home_goals": 1, "away_goals": 1}] * draws
    rows += [{"home_goals": 0, "away_goals": 1}] * away_wins
    return rows


BASE = dict(
    home_team="Brazil", away_team="France",
    home_history=_history(), away_history=_history(),
    h2h=_h2h(), days_rest=4,
)


def test_national_home_advantage():
    f = build_features(**BASE, competition_type="national",
                       home_strength=1823.0, away_strength=1756.0, stage="GROUP")
    assert f["home_advantage"] == 0.1
    assert f["strength_diff"] == pytest.approx(67.0)


def test_club_home_advantage():
    f = build_features(**BASE, competition_type="club_europe",
                       home_strength=850.0, away_strength=620.0, stage="GROUP")
    assert f["home_advantage"] == 0.35
    assert f["strength_diff"] == pytest.approx(230.0)


def test_knockout_flag():
    f_group = build_features(**BASE, competition_type="national",
                             home_strength=1800.0, away_strength=1700.0, stage="GROUP")
    f_knockout = build_features(**BASE, competition_type="national",
                                home_strength=1800.0, away_strength=1700.0, stage="FINAL")
    assert f_group["is_knockout"] == 0
    assert f_knockout["is_knockout"] == 1


def test_feature_keys():
    f = build_features(**BASE, competition_type="national",
                       home_strength=1800.0, away_strength=1700.0, stage="GROUP")
    expected = {
        "home_strength", "away_strength", "strength_diff", "home_advantage",
        "home_form_points", "away_form_points",
        "home_goals_scored_avg", "home_goals_conceded_avg",
        "away_goals_scored_avg", "away_goals_conceded_avg",
        "h2h_home_win_rate", "h2h_avg_goals", "is_knockout", "days_rest",
    }
    assert set(f.keys()) == expected
