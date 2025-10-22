import ast
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
    return list(results.all())


async def update_news(
    session: AsyncSession,
    news: dict,
    news_id: str,
    user_email: str,
) -> None:
    statement = select(News).where(
        News.id == news_id and News.user_email == user_email
    )
    results = await session.exec(statement)
    news_item = results.first()
    if news_item:
        for key, value in news.items():
            if key != "id" and value is not None:
                setattr(news_item, key, value)
        session.add(news_item)
        await session.commit()
        await session.refresh(news_item)


async def like_news(
    session: AsyncSession, news_id: str, email: str
) -> int | None:
    statement = select(News).where(News.id == news_id)
    results = await session.exec(statement)
    news_item = results.first()
    if news_item:
        users = ast.literal_eval(news_item.user_email_list)
        if email not in users:
            users.append(email)
            news_item.user_email_list = str(users)
            news_item.likes += 1
            session.add(news_item)
            await session.commit()
            await session.refresh(news_item)
            return news_item.likes
    return None


async def delete_like(
    session: AsyncSession, news_id: str, email: str
) -> int | None:
    statement = select(News).where(News.id == news_id)
    results = await session.exec(statement)
    news_item = results.first()
    if news_item:
        users = ast.literal_eval(news_item.user_email_list)
        if email in users:
            users.remove(email)
            news_item.user_email_list = str(users)
            news_item.likes -= 1
            session.add(news_item)
            await session.commit()
            await session.refresh(news_item)
            return news_item.likes
    return None
