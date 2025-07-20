import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient



from app.main import app, get_db_session
from app.services.database.database import create_db_and_tables , get_session

from app.services.database.database import init_db , get_session, TestEntry

@pytest.fixture
def test_app() -> FastAPI:
    # Create a mock schema checker
    mock_schema_checker = AsyncMock()
    mock_schema_checker.validate = AsyncMock(return_value=None)
    mock_schema_checker.start = AsyncMock(return_value=None)

    # Add the mock to the app
    app.schema_checker = mock_schema_checker
    return app


@pytest_asyncio.fixture(scope='function')
async def sqlite_client():
    """Create a MongoDB client for the test."""
    #if not sqlcheckfiles():
    DATABASE_FILE = "" # /app/services/database/pynwesdb.db
    DATABASE_URL =  'sqlite+aiosqlite:///'   #   sqlite+aiosqlite:///{SQLITE_PATH}

    init_db()
    ## Retorna classe para chamar uma sessao asincrona 
    return get_session 


@pytest_asyncio.fixture(scope='function')
async def test_database(sqlite_client):
    """Create a test database connection with test collections."""
    # Clean up before each test

    try:
        yield sqlite_client
    finally:
        # Clean up after each test
        sqlite_client #Check method drop SQLite   .drop_database(mongodb_database)


@pytest_asyncio.fixture(scope='function')
async def async_client(test_app: FastAPI, test_database) -> AsyncGenerator:
    """Create an async client for testing."""
    # Mock the authorization dependencies and schema validation
    mock_database = AsyncMock()
    mock_database.client.value = test_database

    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url='http://test'
    ) as client:
        yield client


@pytest.fixture
def mock_headers():
    return {
        'header1': 'value1',
    }