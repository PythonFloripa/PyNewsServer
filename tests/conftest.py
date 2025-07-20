import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient



from app.main import app 
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker

# Importar todos os modelos SQLModel a serem usados (necessários para as validações de modelo)
from app.services.database.database import TestEntry

@pytest.fixture
def test_app() -> FastAPI:
    # Create a mock schema checker
    mock_schema_checker = AsyncMock()
    mock_schema_checker.validate = AsyncMock(return_value=None)
    mock_schema_checker.start = AsyncMock(return_value=None)

    # Add the mock to the app
    app.schema_checker = mock_schema_checker
    return app

 
# --- Configurações do Banco de Dados em Memória para Testes ---
# Usamos engine e AsyncSessionLocal apenas para os testes.
# Isso garante que os testes são isolados e usam o banco de dados em memória.
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine: AsyncEngine = AsyncEngine(create_engine(TEST_DATABASE_URL, echo=False, future=True))

# Fábrica de sessões para os testes
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

async def init_test_db():
    """
    Inicializa o banco de dados em memória para testes, criando todas as tabelas.
    """
    async with test_engine.begin() as conn:
        # Cria as tabelas para todos os modelos SQLModel na base de teste
        await conn.run_sync(SQLModel.metadata.create_all)

async def override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Sobrescreve a dependência get_db_session para usar a sessão de teste.
    """
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture(scope='function')
async def async_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    """
    Cria um cliente assíncrono para testes, com o banco de dados em memória e
    dependências sobrescritas.
    """
    # Sobrescreve a dependência get_db_session no app principal
    test_app.db_session_factory = TestSessionLocal
    test_app.get_db_session = override_get_db_session
    
    # Inicializa o banco de dados em memória e cria as tabelas para cada função de teste
    await init_test_db()

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url='http://test'
    ) as client:
        yield client
    
    # Limpa as tabelas do banco de dados em memória após cada teste
    # ou simplesmente deixa o escopo do fixture fazer isso (memória se autodestrói)
    # se você quiser um ambiente completamente limpo para cada teste, esta linha é redundante
    # para SQLite in-memory, mas é um bom padrão para outros DBs.
    async with test_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
 



@pytest.fixture
def mock_headers():
    return {
        'header1': 'value1',
    }