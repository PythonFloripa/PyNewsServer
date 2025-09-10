import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.enums import LibraryTagUpdatesEnum
from app.services.database.models import Community, Subscription


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
        tags=[LibraryTagUpdatesEnum.BUG_FIX, LibraryTagUpdatesEnum.UPDATE],
        community_id=community.id,
    )
    session.add(subscription)
    await session.commit()

    statement = select(Subscription).where(
        Subscription.email == "teste@teste.com"
    )
    statement = select(Subscription).where(
        Subscription.email == "teste@teste.com"
    )
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.email == "teste@teste.com"
    assert found.tags == [
        LibraryTagUpdatesEnum.BUG_FIX,
        LibraryTagUpdatesEnum.UPDATE,
    ]
    assert found.community_id == community.id


@pytest_asyncio.fixture
async def preset_library(async_client: AsyncClient):
    body1 = {
        "library_name": "Python",
        "releases_url": "http://teste.com/",
        "logo": "http://teste.com/",
    }

    response1 = await async_client.post(
        "/api/libraries",
        json=body1,
        headers={"Content-Type": "application/json"},
    )

    assert response1.status_code == 200

    body2 = {
        "library_name": "Django",
        "releases_url": "http://teste.com/",
        "logo": "http://teste.com/",
    }

    response2 = await async_client.post(
        "/api/libraries",
        json=body2,
        headers={"Content-Type": "application/json"},
    )

    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_post_subscribe_endpoint(async_client: AsyncClient):
    body = {
        "email": "teste@teste.com",
        "tags": ["bug_fix", "updates"],
        "libraries_list": ["Python", "Django"],
    }

    response = await async_client.post(
        "/api/libraries/subscribe",
        json=body,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Subscribed in libraries successfully"
