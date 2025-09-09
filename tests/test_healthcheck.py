from typing import Mapping

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_healthcheck_endpoint(
    async_client: AsyncClient, valid_auth_headers: Mapping[str, str]
):
    """Test the healthcheck endpoint returns correct status and version."""
    # response = await async_client.get(
    #   '/v2/healthcheck', headers=valid_auth_headers
    # )
    response = await async_client.get(
        "/api/healthcheck", headers=valid_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy", "version": "2.0.0"}


@pytest.mark.asyncio
async def test_healthcheck_endpoint_without_auth(async_client: AsyncClient):
    """Test the healthcheck endpoint without authentication headers."""
    # response = await async_client.get('/v2/healthcheck')
    response = await async_client.get("/api/healthcheck")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "healthy", "version": "2.0.0"}
