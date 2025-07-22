import pytest
import pytest_asyncio

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.communities import Community
from app.services.database.libraries import Library

@pytest_asyncio.fixture
async def community(session: AsyncSession):
    community = Community(username="admin", email="a@a.com", password="123")
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return community

@pytest.mark.asyncio
async def test_insert_libraries(session: AsyncSession, community: Community):
   library = Library(
       library_name="DevOps",
       user_email="teste@teste.com",
       releases_url="http://teste.com",
       logo="logo",
       community_id=community.id,
   )
   session.add(library)
   await session.commit()

   statement = select(Library).where(Library.library_name == "DevOps")
   result = await session.exec(statement)
   found = result.first()

   assert found is not None
   assert found.library_name == "DevOps"
   assert found.user_email == "teste@teste.com"
   assert found.releases_url == "http://teste.com"
   assert found.logo == "logo"
   assert found.community_id == community.id
