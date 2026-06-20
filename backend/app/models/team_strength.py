from datetime import datetime
from sqlalchemy import String, Float, DateTime, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class TeamStrength(Base):
    __tablename__ = "team_strengths"
    __table_args__ = (UniqueConstraint("team_name", "competition_type", name="uq_team_strength"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    team_name: Mapped[str] = mapped_column(String, index=True)
    # "national" → FIFA Points | "club_europe" → Squad Value (triệu EUR)
    competition_type: Mapped[str] = mapped_column(String)
    strength_value: Mapped[float] = mapped_column(Float)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
