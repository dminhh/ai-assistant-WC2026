# app/models/match.py
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    competition_id: Mapped[int] = mapped_column(ForeignKey("competitions.id"))
    home_team: Mapped[str] = mapped_column(String)
    away_team: Mapped[str] = mapped_column(String)
    kickoff_time: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # "upcoming" | "live" | "finished"
    status: Mapped[str] = mapped_column(String, default="upcoming")
    home_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    away_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    api_match_id: Mapped[str] = mapped_column(String, unique=True)
