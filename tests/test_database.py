## Test cases for database SQLite using in memory database fixture from conftest.py
#

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select #, SQLModel, create_engine
from httpx import  AsyncClient
#from app.services.database.database import create_test_entry, get_test_entries

@pytest.mark.asyncio
async def test_create_and_read_test_entry(async_client: AsyncClient):
    response = await async_client.post("/test-entry/?message=test_message")
    assert response.status_code == 200
    assert response.json()["message"] == "test_message"
  
    response = await async_client.get("/test-entries/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["message"] == "test_message"