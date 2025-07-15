import os
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient


from app.main import app


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
async def mongodb_client():
    """Create a MongoDB client for the test."""
    mongodb_url = os.getenv('MONGODB_URL', 'mongodb://localhost:27017')
    return AsyncIOMotorClient(mongodb_url)


@pytest_asyncio.fixture(scope='function')
async def test_database(mongodb_client):
    """Create a test database connection with test collections."""
    mongodb_database = os.getenv('MONGODB_DB_CLIENTS', 'test_database')
    db = mongodb_client[mongodb_database]

    # Clean up before each test
    await db.client.drop_database(mongodb_database)

    try:
        yield db
    finally:
        # Clean up after each test
        await db.client.drop_database(mongodb_database)


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
