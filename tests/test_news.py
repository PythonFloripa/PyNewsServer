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
async def news_list(community: Community) -> list[News]:
    news_list = [
        News(
            title="Test news",
            content="A nova versão do Python traz melhorias ...",
            category="release",
            user_email=community.email,
            source_url="https://python.org/news",
            tags="programming",
            social_media_url="https://linkedin.com/pythonista",
            community_id=community.id,
        ),
        News(
            title="Test category",
            content="A nova versão do Python traz melhorias ...",
            category="test_category",
            user_email=community.email,
            source_url="https://python.org/news",
            tags="programming",
            social_media_url="https://linkedin.com/pythonista",
            community_id=community.id,
        ),
        News(
            title="Test user email",
            content="FastAPI agora suporta novas funcionalidades ...",
            category="release",
            user_email="test_user_email@test.com",
            source_url="https://fastapi.com/news",
            tags="programming",
            social_media_url="https://twitter.com/fastapi",
            likes=100,
            community_id=community.id,
        ),
        News(
            title="Test id",
            content="FastAPI agora suporta novas funcionalidades ...",
            category="release",
            user_email=community.email,
            source_url="https://fastapi.com/news",
            tags="programming",
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
    statement = select(News).where(News.title == "Test news")
    result = await session.exec(statement)
    found_news = result.first()
    assert found_news is not None
    assert found_news.title == news_list[0].title
    assert found_news.content == news_list[0].content
    assert found_news.category == news_list[0].category
    assert found_news.user_email == news_list[0].user_email
    assert found_news.source_url == news_list[0].source_url
    assert found_news.tags == news_list[0].tags
    assert found_news.social_media_url == news_list[0].social_media_url
    assert found_news.likes == 0
    assert found_news.community_id == community.id
    assert isinstance(found_news.created_at, datetime)
    assert isinstance(found_news.updated_at, datetime)
    assert found_news.created_at <= datetime.now()
    assert found_news.updated_at >= found_news.created_at


@pytest.mark.asyncio
async def test_post_news_endpoint(
    async_client: AsyncClient, valid_auth_headers: Mapping[str, str]
):
    """Test the news endpoint returns correct status."""
    news_data = {
        "title": "Test News",
        "content": "Test news content.",
        "category": "test_category",
        "source_url": "https://example.com/test-news",
    }
    response = await async_client.post(
        "/api/news", headers=valid_auth_headers, json=news_data
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"status": "News Criada"}


@pytest.mark.asyncio
async def test_insert_news_via_post_news_endpoint(
    session: AsyncSession,
    async_client: AsyncClient,
    community: Community,
    valid_auth_headers: Mapping[str, str],
):
    news_data = {
        "title": "Test News",
        "content": "Test news content.",
        "category": "test_category",
        "tags": "test_tag",
        "source_url": "https://example.com/test-news",
        "social_media_url": "https://test.com/test_news",
    }
    response = await async_client.post(
        "/api/news", json=news_data, headers=valid_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.title == news_data["title"]
    assert stored_news.content == news_data["content"]
    assert stored_news.category == news_data["category"]
    assert stored_news.user_email == community.email
    assert stored_news.source_url == news_data["source_url"]
    assert stored_news.tags == news_data["tags"]
    assert stored_news.social_media_url == news_data["social_media_url"]
    assert stored_news.likes == 0
    assert isinstance(stored_news.created_at, datetime)
    assert isinstance(stored_news.updated_at, datetime)
    assert stored_news.created_at <= datetime.now()
    assert stored_news.updated_at >= stored_news.created_at


@pytest.mark.asyncio
async def test_get_news_endpoint(
    session: AsyncSession,
    async_client: AsyncClient,
    valid_auth_headers: Mapping[str, str],
    news_list: list,
):
    session.add_all(news_list)
    await session.commit()
    response = await async_client.get(
        "/api/news",
        headers=valid_auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in response.json()
    assert len(response.json()["news_list"]) == 3


@pytest.mark.asyncio
async def test_get_news_by_category(
    session: AsyncSession,
    async_client: AsyncClient,
    valid_auth_headers: Mapping[str, str],
    news_list: list,
):
    session.add_all(news_list)
    await session.commit()
    response = await async_client.get(
        "/api/news",
        params={"category": "release"},
        headers=valid_auth_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in data
    assert len(data["news_list"]) == 2
    titles = [news["title"] for news in data["news_list"]]
    assert "Test news" in titles
    assert "Test id" in titles


@pytest.mark.asyncio
async def test_get_news_by_user_email(
    session: AsyncSession,
    async_client: AsyncClient,
    news_list: list,
    valid_auth_headers: Mapping[str, str],
):
    session.add_all(news_list)
    await session.commit()
    response = await async_client.get(
        "/api/news",
        params={},
        headers=valid_auth_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data["news_list"]) == 3
    titles = [news["title"] for news in data["news_list"]]
    assert "Test news" in titles
    assert "Test category" in titles
    assert "Test id" in titles


@pytest.mark.asyncio
async def test_get_news_by_id(
    session: AsyncSession,
    async_client: AsyncClient,
    valid_auth_headers: Mapping[str, str],
    news_list: list,
):
    session.add_all(news_list)
    await session.commit()

    statement = select(News).where(News.title == "Test news")
    result = await session.exec(statement)
    stored_news = result.first()

    response = await async_client.get(
        "/api/news",
        params={"id": stored_news.id},
        headers=valid_auth_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(data["news_list"]) == 1
    assert data["news_list"][0]["id"] == stored_news.id


@pytest.mark.asyncio
async def test_get_news_empty_result(
    async_client: AsyncClient, valid_auth_headers: Mapping[str, str]
):
    response = await async_client.get(
        "/api/news",
        params={"category": "notfound"},
        headers=valid_auth_headers,
    )
    data = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert "news_list" in data
    assert data["news_list"] == []


@pytest.mark.asyncio
async def test_news_integration(
    session: AsyncSession,
    async_client: AsyncClient,
    community: Community,
    valid_auth_headers: Mapping[str, str],
):
    news_data = {
        "title": "Test News",
        "content": "Test news content.",
        "category": "test_category",
        "tags": "test_tag",
        "source_url": "https://example.com/test-news",
        "social_media_url": "https://test.com/test_news",
    }
    post_response = await async_client.post(
        "/api/news", json=news_data, headers=valid_auth_headers
    )
    assert post_response.status_code == status.HTTP_200_OK
    get_response = await async_client.get(
        "/api/news",
        headers=valid_auth_headers,
    )
    data = get_response.json()
    assert get_response.status_code == status.HTTP_200_OK
    assert "news_list" in data
    assert len(data["news_list"]) == 1
    assert data["news_list"][0]["title"] == news_data["title"]
    assert data["news_list"][0]["content"] == news_data["content"]
    assert data["news_list"][0]["category"] == news_data["category"]
    assert data["news_list"][0]["user_email"] == community.email
    assert data["news_list"][0]["source_url"] == news_data["source_url"]
    assert data["news_list"][0]["tags"] == news_data["tags"]
    assert (
        data["news_list"][0]["social_media_url"]
        == news_data["social_media_url"]
    )
    assert data["news_list"][0]["likes"] == 0
