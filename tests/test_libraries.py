import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community, Library


@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest.mark.asyncio
async def test_insert_libraries(session: AsyncSession, community: Community):
    library = Library(
        library_name="Python",
        user_email="teste@teste.com",
        releases_url="http://teste.com",
        logo="logo",
        community_id=community.id,
    )
    session.add(library)
    await session.commit()

    statement = select(Library).where(Library.library_name == "Python")
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.library_name == "Python"
    assert found.user_email == "teste@teste.com"
    assert found.releases_url == "http://teste.com"
    assert found.logo == "logo"
    assert found.community_id == community.id


@pytest.mark.asyncio
async def test_post_libraries_endpoint(
    async_client: AsyncClient, session: AsyncSession
):
    body = {
        "library_name": "Python from API",
        "releases_url": "http://teste.com/",
        "logo": "http://teste.com/",
    }

    response = await async_client.post(
        "/api/libraries",
        json=body,
        headers={"Content-Type": "application/json"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Library created successfully"

    statement = select(Library).where(
        Library.library_name == body["library_name"]
    )
    result = await session.exec(statement)
    created_library = result.first()

    assert created_library is not None
    assert created_library.releases_url == body["releases_url"]
    assert created_library.logo == body["logo"]
