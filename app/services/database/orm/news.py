from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import News


async def create_news(session: AsyncSession, news: dict) -> None:
    _news = News(
        title=news["title"],
        content=news["content"],
        category=news["category"],
        user_email=news["user_email"],
        source_url=news["source_url"],
        tags=news["tags"] or "",
        social_media_url=news["social_media_url"] or "",
        likes=news["likes"],
    )
    session.add(_news)
    await session.commit()
    await session.refresh(_news)


async def get_news_by_query_params(
    session: AsyncSession,
    email: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    id: Optional[str] = None,
) -> list[News]:
    filters = []
    if email is not None:
        filters.append(News.user_email == email)
    if category is not None:
        filters.append(News.category == category)
    if tags is not None:
        filters.append(News.tags == tags)
    if id is not None:
        filters.append(News.id == id)

    statement = select(News).where(*filters)
    results = await session.exec(statement)
    return results.all()


async def like_news(
    session: AsyncSession, news_id: str, user_email: str
) -> int | None:
    statement = select(News).where(News.id == news_id)
    results = await session.exec(statement)
    news_item = results.first()
    if news_item:
        news_item.likes += 1
        session.add(news_item)
        await session.commit()
        await session.refresh(news_item)
        return news_item.likes
    return None
