from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import News


async def get_news_by_query_params(
    session: AsyncSession,
    user_email: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    id: Optional[str] = None,
) -> list[News]:
    filters = []
    if user_email is not None:
        filters.append(News.user_email == user_email)
    if category is not None:
        filters.append(News.category == category)
    if tags is not None:
        filters.append(News.tags == tags)
    if id is not None:
        filters.append(News.id == id)

    print("user_email:", user_email)
    print("Filters:", filters)

    statement = select(News).where(*filters)
    results = await session.exec(statement)
    return results.all()
