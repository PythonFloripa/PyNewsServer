import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from pydantic import BaseModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.routers.authentication import get_current_active_community
from app.services import auth
from app.services.database.models import Community as DBCommunity  # Precisa?
from app.services.database.orm.community import create_community

# ADMIN_USER = os.getenv("ADMIN_USER")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


async def create_community_admin(session: AsyncSession):
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    password = ADMIN_PASSWORD
    hashed_password = auth.hash_password(password)
    community = DBCommunity(
        username=ADMIN_USER,
        email="ADMIN_USER",
        password=hashed_password,
        role="admin",
    )
    session: AsyncSession = session
    session.add(community)
    await session.commit()
    await session.refresh(community)
    return {"msg": "Admin successfully created"}


class CommunityPostResponse(BaseModel):
    status: str = "Community Criado"


def setup():
    router = APIRouter(prefix="/admin", tags=["news"])

    @router.post(
        "create_community",
        response_model=CommunityPostResponse,
        status_code=status.HTTP_200_OK,
        summary="Create Community endpoint",
        description="Create Community and returns a confirmation message",
    )
    async def post_create_community(
        request: Request,
        admin_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        community: Annotated[DBCommunity],
    ):
        """
        Server Admin endpoint that creates Community and returns a confirmation message.
        """
        admin_role = admin_community.get("role")
        if admin_role != "admin":
            return {"status": "Unauthorized"}
        await create_community(
            session=request.app.db_session_factory, community=community
        )

        return CommunityPostResponse()
