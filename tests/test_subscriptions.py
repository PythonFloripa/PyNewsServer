import pytest
import pytest_asyncio

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from services.database.models import Community, Subscription


@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest.mark.asyncio
async def test_insert_subscription(session: AsyncSession, community: Community):
    subscription = Subscription(
        email="teste@teste.com",
        tags="teste,Python",
        community_id=community.id,
    )
    session.add(subscription)
    await session.commit()

    statement = select(Subscription).where(Subscription.email == "teste@teste.com")
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.email == "teste@teste.com"
    assert found.tags == "teste,Python"
    assert found.community_id == community.id
