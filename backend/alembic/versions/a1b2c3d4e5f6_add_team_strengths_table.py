"""add team_strengths table

Revision ID: a1b2c3d4e5f6
Revises: fbe1be876e2e
Create Date: 2026-06-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "fbe1be876e2e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "team_strengths",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("team_name", sa.String(), nullable=False),
        sa.Column("competition_type", sa.String(), nullable=False),
        sa.Column("strength_value", sa.Float(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("team_name", "competition_type", name="uq_team_strength"),
    )
    op.create_index(op.f("ix_team_strengths_team_name"), "team_strengths", ["team_name"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_team_strengths_team_name"), table_name="team_strengths")
    op.drop_table("team_strengths")
