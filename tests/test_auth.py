import pytest
from services.database.models import Community
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


## gerar usuario para autenticação
@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="username", email="username@test.com", password="123Asd!@#")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


## chamar o endpoint de autenticação e validar resposta
@pytest.mark.asyncio
async def test_authentication_token_endpoint(
    async_client: AsyncClient, mock_headers: Mapping[str, str]
):
    """Test the news endpoint returns correct status and version."""
    response = await async_client.post("/api/authentication/token", headers=mock_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "News Criada"}

    