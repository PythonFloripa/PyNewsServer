import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.routers.authentication import get_current_active_community
from app.schemas import CommunityPostResponse
from app.services import auth
from app.services.database.models import Community as DBCommunity  # Precisa?
from app.services.database.orm.community import create_community
from app.services.limiter import limiter

# ADMIN_USER = os.getenv("ADMIN_USER")
# ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")


async def create_admin(session: AsyncSession):
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")
    password = ADMIN_PASSWORD
    hashed_password = auth.hash_password(password)
    community = DBCommunity(
        username=ADMIN_USER,
        email="ADMIN_USER@mail.com",
        password=hashed_password,
        role="admin",
    )
    await create_community(session=session, community=community)

    return {"msg": "Admin successfully created"}


def setup():
    router = APIRouter(prefix="/admin", tags=["admin"])

    @router.post(
        "/create_community",
        response_model=CommunityPostResponse,
        status_code=status.HTTP_201_CREATED,
        summary="Create Community endpoint",
        description="Create Community and returns a confirmation message",
    )
    @limiter.limit("60/minute")
    async def post_create_community(
        request: Request,
        admin_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        community: DBCommunity,
    ):
        """
        Server Admin endpoint that creates Community and returns a confirmation
          message.
        """
        admin_role = admin_community.role
        if admin_role != "admin":
            return {"status": "Unauthorized"}
        session: AsyncSession = request.app.db_session_factory
        await create_community(session=session, community=community)

        return CommunityPostResponse()

    return router
