import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community, LibraryRequest


@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest.mark.asyncio
async def test_insert_libraries(session: AsyncSession, community: Community):
    library = LibraryRequest(
        library_name="Flask",
        user_email="teste@teste.com",
        library_home_page="http://teste.com/",
        community_id=community.id,
    )
    session.add(library)
    await session.commit()

    statement = select(LibraryRequest).where(
        LibraryRequest.library_name == "Flask"
    )
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.user_email == "teste@teste.com"
    assert found.library_home_page == "http://teste.com/"
    assert found.community_id == community.id


@pytest.mark.asyncio
async def test_post_libraries_endpoint(
    async_client: AsyncClient, session: AsyncSession
):
    body = {"library_name": "FastAPI", "library_home_page": "http://teste.com/"}

    response = await async_client.post(
        "/api/libraries/request",
        json=body,
        headers={"Content-Type": "application/json", "user-email": "a@a.com"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Library created successfully"

    statement = select(LibraryRequest).where(
        LibraryRequest.library_name == body["library_name"]
    )
    result = await session.exec(statement)
    created_request = result.first()

    assert created_request is not None
    assert created_request.user_email == "a@a.com"
    assert created_request.library_home_page == "http://teste.com/"
