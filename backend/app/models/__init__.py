# app/models/__init__.py
from app.database import Base
from app.models.competition import Competition
from app.models.match import Match
from app.models.prediction import Prediction
from app.models.user import User
from app.models.team_strength import TeamStrength

__all__ = ["Base", "Competition", "Match", "Prediction", "User", "TeamStrength"]
