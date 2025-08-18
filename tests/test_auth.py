import pytest
import pytest_asyncio
from services.database.models import Community
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from httpx import AsyncClient
from fastapi import status
from typing import Mapping
from app.services.auth import hash_password

password = "123Asd!@#"

## gerar usuario para autenticação
@pytest_asyncio.fixture
async def community(session: AsyncSession):
    hashed_password=hash_password(password)
    community = Community(username="username", email="username@test.com", password=hashed_password)
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest.mark.asyncio
async def test_authentication_token_endpoint(
    async_client: AsyncClient, 
    community: Community # Adicionando a comunidade do fixture
):
    """
    Testa o endpoint de login (/token) com credenciais válidas e inválidas.
    """
    # 1. Teste de login com credenciais válidas
    # O OAuth2PasswordRequestForm espera 'username' e 'password'
    form_data = {
        "username": community.username, 
        "password":  password
    }
    
    response = await async_client.post(
        "/api/authentication/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    # Validar a resposta
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "Bearer"

    # 2. Teste de login com credenciais inválidas
    invalid_form_data = {
        "username": "wrong_username", 
        "password": "wrong_password"
    }

    response_invalid = await async_client.post(
        "/api/authentication/token",
        data=invalid_form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    
    # Validar que o status é 401 Unauthorized
    assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_invalid.json()["detail"] == "Credenciais inválidas"

