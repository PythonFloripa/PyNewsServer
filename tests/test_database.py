## Test cases for database SQLite using in memory database fixture from conftest.py
#

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlmodel import Session, select #, SQLModel, create_engine
from httpx import  AsyncClient 

@pytest.mark.asyncio
async def test_create_and_read_test_entry(async_client: AsyncClient):
    response = await async_client.post("/test-entry/?message=test_message")
    assert response.status_code == 200
    assert response.json()["message"] == "test_message"
  
    response = await async_client.get("/test-entries/")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["message"] == "test_message"



@pytest.mark.asyncio
async def test_session_isolation_and_db_reset(async_client: AsyncClient):
    """
    Testa se as sessões são isoladas e se o banco de dados de teste é reiniciado
    entre as chamadas do cliente assíncrono.

    Este teste usa o `async_client` para simular requisições HTTP, garantindo
    que a dependência de sessão seja sobrescrita e o DB limpo a cada teste.
    """

    print("\n--- Segunda Interação: Verificando banco de dados limpo ---")
    response_get_part2 = await async_client.get("/test-entries/")
    assert response_get_part2.status_code == 200
    print(f"Dados encontrados na segunda interação (esperado 0): {response_get_part2.json()}")
    print("Banco de dados reiniciado com sucesso entre os testes.")
    assert len(response_get_part2.json()) == 0
