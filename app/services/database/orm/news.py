from typing import Optional

from services.database.models import News
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession


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
