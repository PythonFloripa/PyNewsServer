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
        user_email="teste@teste.com",
        tags=[LibraryTagUpdatesEnum.BUG_FIX, LibraryTagUpdatesEnum.UPDATE],
        community_id=community.id,
    )
    session.add(subscription)
    await session.commit()

    statement = select(Subscription).where(
        Subscription.user_email == "teste@teste.com"
    )
    statement = select(Subscription).where(
        Subscription.user_email == "teste@teste.com"
    )
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.user_email == "teste@teste.com"
    assert found.tags == [
        LibraryTagUpdatesEnum.BUG_FIX,
        LibraryTagUpdatesEnum.UPDATE,
    ]
    assert found.community_id == community.id


async def preset_libraries_with_http_post(async_client: AsyncClient):
    body1 = {
        "library_name": "Flask",
        "news": [
            {"tag": "updates", "description": "Updated"},
            {"tag": "bug_fix", "description": "Fixed"},
        ],
        "logo": "http://teste.com/",
        "version": "3.11",
        "release_date": "2025-01-01",
        "releases_doc_url": "http://teste.com/",
        "fixed_release_url": "http://teste.com/",
        "language": "Python",
    }

    response1 = await async_client.post(
        "/api/libraries",
        json=body1,
        headers={"Content-Type": "application/json"},
    )

    assert response1.status_code == 200

    body2 = {
        "library_name": "Django",
        "news": [
            {"tag": "updates", "description": "Updated"},
            {"tag": "bug_fix", "description": "Fixed"},
        ],
        "logo": "http://teste.com/",
        "version": "3.11",
        "release_date": "2025-01-01",
        "releases_doc_url": "http://teste.com/",
        "fixed_release_url": "http://teste.com/",
        "language": "Python",
    }

    response2 = await async_client.post(
        "/api/libraries",
        json=body2,
        headers={"Content-Type": "application/json"},
    )

    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_post_subscribe_endpoint(
    async_client: AsyncClient, session: AsyncSession
):
    await preset_libraries_with_http_post(async_client=async_client)

    body = {
        "tags": ["bug_fix", "updates"],
        "libraries_list": ["Flask", "Django"],
    }

    response = await async_client.post(
        "/api/libraries/subscribe",
        json=body,
        headers={"Content-Type": "application/json", "user-email": "a@a.com"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Subscribed in libraries successfully"

    statement = select(Subscription).where(Subscription.user_email == "a@a.com")
    result = await session.exec(statement)
    created_subscriptions = result.all()

    assert created_subscriptions is not None
    assert len(created_subscriptions) == 2
    assert created_subscriptions[0].tags == [
        LibraryTagUpdatesEnum.BUG_FIX,
        LibraryTagUpdatesEnum.UPDATE,
    ]
    assert created_subscriptions[1].tags == [
        LibraryTagUpdatesEnum.BUG_FIX,
        LibraryTagUpdatesEnum.UPDATE,
    ]


@pytest.mark.asyncio
async def test_post_subscribe_endpoint_with_unexistents_libraries(
    async_client: AsyncClient,
):
    await preset_libraries_with_http_post(async_client=async_client)

    body = {
        "tags": ["bug_fix", "updates"],
        "libraries_list": ["Python", "NodeJS"],
    }

    response = await async_client.post(
        "/api/libraries/subscribe",
        json=body,
        headers={"Content-Type": "application/json", "user-email": "a@a.com"},
    )

    assert response.status_code == 404
