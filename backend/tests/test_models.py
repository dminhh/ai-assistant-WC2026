import pytest
from app.models.competition import Competition
from app.models.match import Match


@pytest.mark.asyncio
async def test_create_competition(db_session):
    comp = Competition(
        name="FIFA World Cup 2026",
        api_competition_id="2000",
        is_active=True,
        country="World",
        season="2026",
    )
    db_session.add(comp)
    await db_session.commit()
    await db_session.refresh(comp)
    assert comp.id is not None
    assert comp.is_active is True
