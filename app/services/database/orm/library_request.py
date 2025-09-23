from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models.libraries_request import LibraryRequest


async def insert_library_request(
    library_request: LibraryRequest,
    session: AsyncSession,
):
    session.add(library_request)
    await session.commit()
    await session.refresh(library_request)


async def get_all_library_requests(
    session: AsyncSession,
) -> List[LibraryRequest]:
    statement = select(LibraryRequest)
    result = await session.exec(statement)
    return [library_request for library_request in result.all()]
