from collections.abc import AsyncGenerator, Generator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.main import app as fastapi_app
from app.main import get_db_session

# Importar todos os modelos SQLModel a serem usados
# (necessários para as validações de modelo)

# --- Configurações do Banco de Dados em Memória para Testes ---
# Usamos engine e AsyncSessionLocal apenas para os testes.
# Isso garante que os testes são isolados e usam o banco de dados em memória.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

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


@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async_session_generator = get_db_session_test()
    session = await anext(async_session_generator)
    yield session
    await session.close()


@pytest.fixture
def test_app() -> Generator[FastAPI]:
    # Create a mock schema checker
    mock_schema_checker = AsyncMock()
    mock_schema_checker.validate = AsyncMock(return_value=None)
    mock_schema_checker.start = AsyncMock(return_value=None)

    # Add the mock to the app
    fastapi_app.schema_checker = mock_schema_checker
    fastapi_app.dependency_overrides[get_db_session] = get_db_session_test
    yield fastapi_app
    fastapi_app.dependency_overrides.clear()


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


@pytest.fixture
def mock_headers():
    return {
        "header1": "value1",
    }
