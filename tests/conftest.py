import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi import FastAPI, status
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app
from app.services.auth import hash_password
from app.services.database.models.communities import Community
from app.services.encryption import encrypt_email

# from app.main import get_db_session

# Importar todos os modelos SQLModel a serem usados
# (necessários para as validações de modelo)

# --- Configurações do Banco de Dados em Memória para Testes ---
# Usamos engine e AsyncSessionLocal apenas para os testes.
# Isso garante que os testes são isolados e usam o banco de dados em memória.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
os.environ["ADMIN_USER"] = "ADMIN_USER"
os.environ["ADMIN_PASSWORD"] = "ADMIN_PASSWORD"
os.environ["ADMIN_EMAIL"] = "ADMIN_EMAIL"


test_engine = create_async_engine(TEST_DATABASE_URL, echo=False, future=True)

# Fábrica de sessões para os testes
TestSessionLocal = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


async def get_db_session_test() -> AsyncGenerator[AsyncSession, None]:
    """
    Sobrescreve a dependência get_db_session para usar a sessão de teste.
    """
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async_session_generator = get_db_session_test()
    session = await anext(async_session_generator)  # noqa: F821
    yield session
    await session.close()


@pytest_asyncio.fixture
async def test_app(session) -> FastAPI:
    mock_db_connection = session
    setattr(app, "db_session_factory", mock_db_connection)
    return app


@pytest_asyncio.fixture(scope="function")
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Cria um cliente assíncrono para testes, com o banco de dados em memória e
    dependências sobrescritas.
    """
    # Sobrescreve a dependência get_db_session no app principal
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        yield client


class CommunityCredentials:
    username: str = "community_username"
    email: str = "community_name@test.com"
    password: str = "community_password"
    hashed_password: str = hash_password(password)


@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(
        username=CommunityCredentials.username,
        email=encrypt_email(CommunityCredentials.email),
        password=CommunityCredentials.hashed_password,
    )
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest_asyncio.fixture()
async def token(async_client: AsyncClient) -> str:
    form_data = {
        "grant_type": "password",
        "username": CommunityCredentials.username,
        "password": CommunityCredentials.password,
    }
    token_response = await async_client.post(
        "/api/authentication/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_response.status_code == status.HTTP_200_OK
    return token_response.json()["access_token"]


@pytest.fixture
def valid_auth_headers(community: Community, token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "user-email": CommunityCredentials.email,
    }
