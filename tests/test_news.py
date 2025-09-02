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
async def community(session: AsyncSession) -> Community:
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community


@pytest_asyncio.fixture
async def news_list(community: Community) -> list[News]:
    news_list = [
        News(
            title="Python 3.12 Lançado!",
            content="A nova versão do Python traz melhorias ...",
            category="release",
            user_email="dev@example.com",
            source_url="https://python.org/news",
            tags="python, release, programming",
            social_media_url="https://linkedin.com/pythonista",
            community_id=community.id,  # Usando o ID da comunidade do fixture
        ),
        News(
            title="FastAPI 0.100 Lançado!",
            content="FastAPI agora suporta novas funcionalidades ...",
            category="release",
            user_email="example@pynews.com",
            source_url="https://fastapi.com/news",
            tags="fastapi, release, web",
            social_media_url="https://twitter.com/fastapi",
            likes=100,
        ),
    ]
    return news_list


@pytest.mark.asyncio
async def test_insert_news(
    session: AsyncSession, community: Community, news_list: list
):
    """
    Testa a inserção de uma notícia no banco de dados.
    """
    session.add(news_list[0])
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


@pytest.mark.asyncio
async def test_post_news_endpoint(
    async_client: AsyncClient, mock_headers: Mapping[str, str]
):
    """Test the news endpoint returns correct status."""
    response = await async_client.post("/api/news", headers=mock_headers)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "News Criada"}


@pytest.mark.asyncio
async def test_get_news_endpoint(
    session: AsyncSession,
    async_client: AsyncClient,
    mock_headers: Mapping[str, str],
    news_list: list,
):
    session.add(news_list[0])
    session.add(news_list[1])
    await session.commit()

    """Test the news endpoint returns correct status and version."""
    response = await async_client.get(
        "/api/news",
        headers=mock_headers,
    )

    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in response.json()
    assert len(response.json()["news_list"]) == 2


@pytest.mark.asyncio
async def test_get_news_by_category(
    session: AsyncSession,
    async_client: AsyncClient,
    mock_headers: Mapping[str, str],
    news_list: list,
):
    # Add news to DB
    session.add_all(news_list)
    await session.commit()

    # Filter by category
    response = await async_client.get(
        "/api/news",
        params={"category": "release"},
        headers={"Content-Type": "application/json"},
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in data
    assert len(data["news_list"]) == 2
    titles = [news["title"] for news in data["news_list"]]
    assert "Python 3.12 Lançado!" in titles
    assert "FastAPI 0.100 Lançado!" in titles


@pytest.mark.asyncio
async def test_get_news_by_user_email(
    session: AsyncSession, async_client: AsyncClient, news_list: list
):
    session.add_all(news_list)
    await session.commit()

    response = await async_client.get(
        "/api/news",
        params={},
        headers={
            "Content-Type": "application/json",
            "user-email": "dev@example.com",
        },
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data["news_list"]) == 1
    assert data["news_list"][0]["user_email"] == "dev@example.com"
    assert data["news_list"][0]["title"] == "Python 3.12 Lançado!"


@pytest.mark.asyncio
async def test_get_news_by_id(
    session: AsyncSession,
    async_client: AsyncClient,
    mock_headers: Mapping[str, str],
    news_list: list,
):
    session.add_all(news_list)
    await session.commit()
    # Get the id from DB
    statement = select(News).where(News.title == "Python 3.12 Lançado!")
    result = await session.exec(statement)
    news = result.first()
    response = await async_client.get(
        "/api/news",
        params={"id": news.id},
        headers=mock_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data["news_list"]) == 1
    assert data["news_list"][0]["id"] == news.id
    assert data["news_list"][0]["title"] == "Python 3.12 Lançado!"


@pytest.mark.asyncio
async def test_get_news_empty_result(
    async_client: AsyncClient, mock_headers: Mapping[str, str]
):
    response = await async_client.get(
        "/api/news",
        params={"category": "notfound"},
        headers=mock_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in data
    assert data["news_list"] == []


# ADD like test case for News model
