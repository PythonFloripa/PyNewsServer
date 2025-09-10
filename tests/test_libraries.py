from datetime import date

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.enums import LibraryTagUpdatesEnum
from app.schemas import LibraryNews
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
        library_name="Flask",
        news=[
            LibraryNews(
                tag=LibraryTagUpdatesEnum.UPDATE, description="Updated"
            ).model_dump(),
            LibraryNews(
                tag=LibraryTagUpdatesEnum.BUG_FIX, description="Fixed"
            ).model_dump(),
        ],
        logo="http://teste.com/",
        version="3.11",
        release_date=date.today(),
        releases_doc_url="http://teste.com/",
        fixed_release_url="http://teste.com/",
        language="Python",
        community_id=community.id,
    )
    session.add(library)
    await session.commit()

    statement = select(Library).where(Library.library_name == "Flask")
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert len(found.news) == 2
    assert found.logo == "http://teste.com/"
    assert found.version == "3.11"
    assert found.release_date == date.today()
    assert found.releases_doc_url == "http://teste.com/"
    assert found.fixed_release_url == "http://teste.com/"
    assert found.language == "Python"
    assert found.community_id == community.id


@pytest.mark.asyncio
async def test_post_libraries_endpoint(
    async_client: AsyncClient, session: AsyncSession
):
    body = {
        "library_name": "FastAPI",
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
    assert created_library.language == body["language"]
    assert len(created_library.news) == len(body["news"])


@pytest.mark.asyncio
async def test_get_libraries_by_language(async_client: AsyncClient):
    body = {
        "library_name": "FastAPI",
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

    responsePOST = await async_client.post(
        "/api/libraries",
        json=body,
        headers={"Content-Type": "application/json"},
    )

    assert responsePOST.status_code == 200
    assert responsePOST.json()["status"] == "Library created successfully"

    response = await async_client.get(
        "/api/libraries",
        params={"language": "Python"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["library_name"] == "FastAPI"
    assert len(data[0]["news"]) == 2
    assert data[0]["news"][0]["tag"] == "updates"
    assert data[0]["news"][0]["description"] == "Updated"
    assert data[0]["news"][1]["tag"] == "bug_fix"
    assert data[0]["news"][1]["description"] == "Fixed"
    assert data[0]["logo"] == "http://teste.com/"
    assert data[0]["version"] == "3.11"
    assert data[0]["release_date"] == "2025-01-01"
    assert data[0]["releases_doc_url"] == "http://teste.com/"
    assert data[0]["fixed_release_url"] == "http://teste.com/"
    assert data[0]["language"] == "Python"


@pytest.mark.asyncio
async def test_get_libraries_by_inexistent_language(async_client: AsyncClient):
    body = {
        "library_name": "FastAPI",
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

    responsePOST = await async_client.post(
        "/api/libraries",
        json=body,
        headers={"Content-Type": "application/json"},
    )

    assert responsePOST.status_code == 200
    assert responsePOST.json()["status"] == "Library created successfully"

    response = await async_client.get(
        "/api/libraries",
        params={"language": "NodeJS"},
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 0
