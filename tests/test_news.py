from datetime import datetime
from typing import Mapping

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient
from services.database.models import Community, News
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest.mark.asyncio
async def test_insert_news(session: AsyncSession, community: Community):
    """
    Testa a inserção de uma notícia no banco de dados.
    """
    news = News(
      title="Python 3.12 Lançado!",
      content="A nova versão do Python traz melhorias ...",
      category="release",
      user_email="dev@example.com",
      source_url="https://python.org/news",
      tags="python, release, programming",
      social_media_url="https://linkedin.com/pythonista",
      community_id=community.id,  # Usando o ID da comunidade do fixture
    )
    session.add(news)
    await session.commit()

    statement = select(News).where(News.title == "Python 3.12 Lançado!")
    result = await session.exec(statement)
    found_news = result.first()

    assert found_news is not None
    assert found_news.title == "Python 3.12 Lançado!"
    assert found_news.content == "A nova versão do Python traz melhorias ..."
    assert found_news.category == "release"
    assert found_news.user_email == "dev@example.com"
    assert found_news.source_url == "https://python.org/news"
    assert found_news.tags == "python, release, programming"
    assert found_news.social_media_url == "https://linkedin.com/pythonista"
    assert found_news.likes == 0
    assert found_news.community_id == community.id
    assert isinstance(found_news.created_at, datetime)
    assert isinstance(found_news.updated_at, datetime)
    assert found_news.created_at <= datetime.now()
    assert found_news.updated_at >= found_news.created_at


# ADD like test case for News model

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
