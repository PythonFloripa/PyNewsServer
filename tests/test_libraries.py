from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from services.database.models import Community, Library
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


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
        logo="http://teste.com",
        version="3.12",
        release_date=date.today(),
        releases_doc_url="http://teste.com",
        fixed_release_url="http://teste.com",
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
    assert found.logo == "http://teste.com"
    assert found.version == "3.12"
    assert found.release_date == date.today()
    assert found.releases_doc_url == "http://teste.com"
    assert found.fixed_release_url == "http://teste.com"
    assert found.community_id == community.id


@pytest.mark.asyncio
async def test_post_libraries_endpoint(
    async_client: AsyncClient, session: AsyncSession
):
    body = {
        "library_name": "Python from API",
        "news": [
            {"tag": "updates", "description": "New feature"},
            {"tag": "bug_fix", "description": "Fixed bug"},
        ],
        "logo": "http://teste.com/",
        "version": "3.12",
        "release_date": "2023-01-01",
        "releases_doc_url": "http://teste.com/",
        "fixed_release_url": "http://teste.com/",
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
    assert created_library.logo == body["logo"]
    assert created_library.version == body["version"]
    assert created_library.release_date == date.fromisoformat(
        body["release_date"]
    )
    assert created_library.releases_doc_url == body["releases_doc_url"]
    assert created_library.fixed_release_url == body["fixed_release_url"]
