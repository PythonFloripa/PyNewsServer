import pytest
from fastapi import status
from httpx import AsyncClient

from app.services.database.models import Community
from tests.conftest import CommunityCredentials


@pytest.mark.asyncio
async def test_authentication_token_endpoint(
    async_client: AsyncClient,
    community: Community,  # Adicionando a comunidade do fixture
):
    """
    Testa o endpoint de login (/token) com credenciais válidas e inválidas.
    """
    # 1. Teste de login com credenciais válidas
    # O OAuth2PasswordRequestForm espera 'username' e 'password'
    form_data = {
        "username": CommunityCredentials.username,
        "password": CommunityCredentials.password,
    }

    response = await async_client.post(
        "/api/authentication/token",
        data=form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Validar a resposta
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert "token_type" in response.json()
    assert response.json()["token_type"] == "Bearer"

    # 2. Teste de login com credenciais inválidas
    invalid_form_data = {
        "username": "wrong_username",
        "password": "wrong_password",
    }

    response_invalid = await async_client.post(
        "/api/authentication/token",
        data=invalid_form_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    # Validar que o status é 401 Unauthorized
    assert response_invalid.status_code == status.HTTP_401_UNAUTHORIZED
    assert response_invalid.json()["detail"] == "Credenciais inválidas"


@pytest.mark.asyncio
async def test_community_me_with_valid_token(
    async_client: AsyncClient,
    community: Community,
):
    """
    Testa se o endpoint protegido /authenticate/me/ retorna os dados do usuário
    com um token válido.
    """
    # 1. Obter um token de acesso primeiro
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
    token = token_response.json()["access_token"]

    # 2. Acessar o endpoint protegido com o token
    headers = {"Authorization": f"Bearer {token}"}
    response = await async_client.get("/api/authentication/me", headers=headers)

    # Validar a resposta
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["username"] == CommunityCredentials.username
    assert user_data["email"] == CommunityCredentials.email
    # Assegurar que a senha não é retornada na resposta
    assert "password" not in user_data


@pytest.mark.asyncio
async def test_community_me_without_token(async_client: AsyncClient):
    """
    Testa se o endpoint protegido authentication/me/ retorna um erro 401 sem um token de acesso.
    """
    response = await async_client.get("/api/authentication/me")

    # Validar a resposta
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.asyncio
async def test_community_me_with_bad_token(async_client: AsyncClient):
    """
    Testa se o endpoint protegido authentication/me/ retorna um erro 401 sem um token de acesso.
    """
    headers = {"Authorization": "Bearer WrongToken"}
    response = await async_client.get("/api/authentication/me", headers=headers)

    # Validar a resposta
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "detail" in response.json()
    assert response.json()["detail"] == "Could not validate credentials"
