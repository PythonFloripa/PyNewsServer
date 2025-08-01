from typing import Mapping

import pytest
from fastapi import status
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_news_endpoint(
    async_client: AsyncClient, mock_headers: Mapping[str, str]
):
    """Test the news endpoint returns correct status and version."""
    response = await async_client.post("/api/news", headers=mock_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "News Criada"}


@pytest.mark.asyncio
async def test_news_endpoint_without_auth(async_client: AsyncClient):
    """Test the news endpoint without authentication headers."""
    response = await async_client.post("/api/news")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "News Criada"}
