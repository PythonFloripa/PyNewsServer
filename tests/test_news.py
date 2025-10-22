from datetime import datetime
from typing import Mapping

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.routers.news.routes import encode_email
from app.services.database.models import Community, News
from tests.conftest import CommunityCredentials


@pytest_asyncio.fixture
async def news_list(community: Community) -> list[News]:
    news_list = [
        News(
            title="Test news",
            content="A nova versão do Python traz melhorias ...",
            category="release",
            user_email=CommunityCredentials.email,
            source_url="https://python.org/news",
            tags="programming",
            social_media_url="https://linkedin.com/pythonista",
            community_id=community.id,
        ),
        News(
            title="Test category",
            content="A nova versão do Python traz melhorias ...",
            category="test_category",
            user_email=CommunityCredentials.email,
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
            user_email=CommunityCredentials.email,
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
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.title == news_list[0].title
    assert stored_news.content == news_list[0].content
    assert stored_news.category == news_list[0].category
    assert stored_news.user_email == news_list[0].user_email
    assert stored_news.source_url == news_list[0].source_url
    assert stored_news.tags == news_list[0].tags
    assert stored_news.social_media_url == news_list[0].social_media_url
    assert stored_news.likes == 0
    assert stored_news.community_id == community.id
    assert isinstance(stored_news.created_at, datetime)
    assert isinstance(stored_news.updated_at, datetime)
    assert stored_news.created_at <= datetime.now()
    assert stored_news.updated_at >= stored_news.created_at
    assert stored_news.publish is False


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
    response: Response = await async_client.post(
        url="/api/news", headers=valid_auth_headers, json=news_data
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
    assert stored_news.user_email == CommunityCredentials.email
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
    assert stored_news is not None

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
    assert data["news_list"][0]["user_email"] == CommunityCredentials.email
    assert data["news_list"][0]["source_url"] == news_data["source_url"]
    assert data["news_list"][0]["tags"] == news_data["tags"]
    assert (
        data["news_list"][0]["social_media_url"]
        == news_data["social_media_url"]
    )
    assert data["news_list"][0]["likes"] == 0


@pytest.mark.asyncio
async def test_put_news_endpoint(
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
    assert stored_news is not None
    assert stored_news.publish is False

    data: dict = {
        "title": "updated title",
        "content": "updated content",
        "category": "updated_category",
        "source_url": "https://updated_url.com",
        "tags": "test_tag_updated",
        "social_media_url": "https://updated_social_media_url.com",
    }

    response: Response = await async_client.put(
        url=f"/api/news/{stored_news.id}",
        headers=valid_auth_headers,
        json={
            "title": data["title"],
            "content": data["content"],
            "category": data["category"],
            "source_url": data["source_url"],
            "tags": data["tags"],
            "social_media_url": data["social_media_url"],
            "publish": True,
        },
    )
    assert response.status_code == status.HTTP_200_OK

    statement = select(News).where(News.title == data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.content == data["content"]
    assert stored_news.category == data["category"]
    assert stored_news.user_email == valid_auth_headers["user-email"]
    assert stored_news.source_url == data["source_url"]
    assert stored_news.tags == data["tags"]
    assert stored_news.social_media_url == data["social_media_url"]
    assert stored_news.publish


@pytest.mark.asyncio
async def test_news_likes_endpoint(
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
    response: Response = await async_client.post(
        url="/api/news", json=news_data, headers=valid_auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.likes == 0

    emails = ["like@test.com", "like2@test.com"]

    # Add likes
    response: Response = await async_client.post(
        url=f"/api/news/{stored_news.id}/like",
        json={"email": emails[0]},
        headers={**valid_auth_headers, "user-email": emails[0]},
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.likes == 1
    assert stored_news.user_email_list == f"['{encode_email(emails[0])}']"

    response: Response = await async_client.post(
        url=f"/api/news/{stored_news.id}/like",
        headers={**valid_auth_headers, "user-email": emails[1]},
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.likes == 2
    assert (
        stored_news.user_email_list
        == f"['{encode_email(emails[0])}', '{encode_email(emails[1])}']"
    )

    # Remove likes
    response: Response = await async_client.delete(
        url=f"/api/news/{stored_news.id}/like",
        headers={**valid_auth_headers, "user-email": emails[0]},
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.likes == 1
    assert stored_news.user_email_list == f"['{encode_email(emails[1])}']"

    response: Response = await async_client.delete(
        url=f"/api/news/{stored_news.id}/like",
        headers={**valid_auth_headers, "user-email": emails[1]},
    )
    assert response.status_code == status.HTTP_200_OK
    statement = select(News).where(News.title == news_data["title"])
    result = await session.exec(statement)
    stored_news = result.first()
    assert stored_news is not None
    assert stored_news.likes == 0
    assert stored_news.user_email_list == "[]"


@pytest.mark.asyncio
async def test_news_endpoint_blocks_unauthorized_access(
    async_client: AsyncClient,
):
    news_data = {
        "title": "Test News",
        "content": "Test news content.",
        "category": "test_category",
        "tags": "test_tag",
        "source_url": "https://example.com/test-news",
        "social_media_url": "https://test.com/test_news",
    }
    response: Response = await async_client.post(
        url="/api/news", json=news_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: Response = await async_client.get(url="/api/news")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: Response = await async_client.put(
        url="/api/news/1", json=news_data
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: Response = await async_client.post(url="/api/news/1/like")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    response: Response = await async_client.delete(url="/api/news/1/like")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED