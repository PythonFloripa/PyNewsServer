import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlmodel import Field, Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.main import app
from app.services.database.database import get_session 


@pytest.fixture
def test_app() -> FastAPI:
    # Create a mock schema checker
    mock_schema_checker = AsyncMock()
    mock_schema_checker.validate = AsyncMock(return_value=None)
    mock_schema_checker.start = AsyncMock(return_value=None)

    # Add the mock to the app
    app.schema_checker = mock_schema_checker
    return app


@pytest.fixture
def mock_headers():
    return {
        'header1': 'value1',
    }

class Test(SQLModel, table=True):
    """
    Modelo de teste para o banco de dados em memória.
    Representa uma tabela simples para operações de CRUD.
    """
    id: int | None = Field(default=None, primary_key=True)
    test_index_string: str = Field(default='default_index', index=True)
    test_string: str = Field(default='test_string', index=False)


# Nova fixture que retorna a CLASSE Test
@pytest.fixture(name="test_model_class")
def test_model_class_fixture():
    """
    Fornece a classe SQLModel 'Test' para os testes,
    evitando a necessidade de importá-la diretamente.
    """
    return Test


@pytest.fixture(name="session")
def session_fixture():
    ###  create_engine("sqlite://",... ) creates an in-memory SQLite db 
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
 
@pytest.fixture(name="client")
def client_fixture(session: Session,  test_app: FastAPI):
    def get_session_override():
        return session
    test_app.dependency_overrides[get_session] = get_session_override
    client = TestClient(test_app)
    yield client
    test_app.dependency_overrides.clear()


@pytest_asyncio.fixture(name="async_client", scope='function')
async def async_client_fixture(test_app: FastAPI, session: Session) -> AsyncGenerator:
    """
    Cria um cliente assíncrono para testes de unidade,
    garantindo que a sessão do banco de dados em memória seja utilizada.
    """
    def get_session_override():
        yield session 
    test_app.dependency_overrides[get_session] = get_session_override
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url='http://test'
    ) as client:
        yield client
    test_app.dependency_overrides.clear()