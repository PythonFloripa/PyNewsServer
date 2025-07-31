from datetime import datetime

import pytest
import pytest_asyncio
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
async def test_insert_libraries(session: AsyncSession, community: Community):
    """
    Testa a inserção de uma notícia no banco de dados.
    """
    news = News(
      title="Python 3.12 Lançado!",
      content="A nova versão do Python traz melhorias ...",
      author="Python Team",
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
    assert found_news.author == "Python Team"
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
