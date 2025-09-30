from typing import List

from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Library


async def insert_library(
    library: Library,
    session: AsyncSession,
) -> Library:
    session.add(library)
    await session.commit()
    await session.refresh(library)
    return library


async def get_library_ids_by_multiple_names(
    names: List[str],
    session: AsyncSession,
) -> List[int]:
    lower_case_names = [name.lower() for name in names]
    statement = select(Library.id).where(
        func.lower(Library.library_name).in_(lower_case_names)
    )
    result = await session.exec(statement)
    return [id for id in result.all() if id is not None]


async def get_libraries_by_language(
    language: str,
    session: AsyncSession,
) -> List[Library]:
    statement = select(Library).where(
        func.lower(Library.language) == language.lower()
    )
    result = await session.exec(statement)
    return [library for library in result.all()]
