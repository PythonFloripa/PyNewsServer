# app/services/database/community.py
from sqlmodel import select
from sqlalchemy.exc import NoResultFound
from app.services.database.model.community_model import Community
from app.services.database.database import get_session

async def get_community_by_username(username: str):
    async for session in get_session():
        stmt = select(Community).where(Community.username == username)
        result = await session.exec(stmt)
        user = result.one_or_none()
        return user
