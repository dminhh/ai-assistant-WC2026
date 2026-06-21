from datetime import datetime
from sqlalchemy import String, Integer, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TeamHistory(Base):
    __tablename__ = "team_history"
    __table_args__ = (UniqueConstraint("team_name", "match_date", "opponent", name="uq_team_history"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(String, index=True)
    opponent: Mapped[str] = mapped_column(String)
    result: Mapped[str] = mapped_column(String)        # W / D / L
    goals_scored: Mapped[int] = mapped_column(Integer)
    goals_conceded: Mapped[int] = mapped_column(Integer)
    match_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
