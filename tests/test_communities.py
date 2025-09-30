import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community


@pytest.mark.asyncio
async def test_insert_communities(session: AsyncSession):
    community = Community(
        username="admin",
        email="teste@teste.com",
        password="@teste123",
    )
    session.add(community)
    await session.commit()
    await session.refresh(community)

    statement = select(Community).where(Community.username == "admin")
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.username == "admin"
    assert found.email == "teste@teste.com"
    assert found.password == "@teste123"
