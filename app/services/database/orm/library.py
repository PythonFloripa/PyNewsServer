from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models.libraries import Library


async def insert_library(
    library: Library,
    session: AsyncSession,
):
    session.add(library)
    await session.commit()
    await session.refresh(library)
    return library
