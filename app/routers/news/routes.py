from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.params import Header
from pydantic import BaseModel

from app.routers.authentication import get_current_active_community
from app.schemas import News
from app.services.database.models import Community as DBCommunity
from app.services.database.orm.news import (
    create_news,
    get_news_by_query_params,
    like_news,
)


class NewsPostResponse(BaseModel):
    status: str = "News Criada"


class NewsGetResponse(BaseModel):
    status: str = "Lista de News Obtida"
    news_list: list = []


class NewsLikeResponse(BaseModel):
    total_likes: int | None


def setup():
    router = APIRouter(prefix="/news", tags=["news"])

    @router.post(
        "",
        response_model=NewsPostResponse,
        status_code=status.HTTP_200_OK,
        summary="News endpoint",
        description="Creates news and returns a confirmation message",
    )
    async def post_news(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        news: News,
        user_email: str = Header(..., alias="user-email"),
    ):
        """
        News endpoint that creates news and returns a confirmation message.
        """
        news_dict = news.__dict__
        news_dict["user_email"] = user_email
        await create_news(
            session=request.app.db_session_factory, news=news_dict
        )
        return NewsPostResponse()

    @router.get(
        "",
        response_model=NewsGetResponse,
        status_code=status.HTTP_200_OK,
        summary="Get News",
        description="Retrieves news filtered by user and query params",
    )
    async def get_news(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        id: str | None = None,
        user_email: str = Header(..., alias="user-email"),
        category: str | None = None,
        tags: str | None = None,
    ):
        """
        Get News endpoint that retrieves news filtered by user and query params.
        """
        news_list = await get_news_by_query_params(
            session=request.app.db_session_factory,
            id=id,
            email=user_email,
            category=category,
            tags=tags,
        )
        return NewsGetResponse(news_list=news_list)

    @router.post(
        path="/{news_id}/like",
        response_model=NewsPostResponse,
        status_code=status.HTTP_200_OK,
        summary="News like endpoint",
        description="Allows user to like a news item",
    )
    async def post_like(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        news_id,
        user_email: str = Header(..., alias="user-email"),
    ):
        """
        News endpoint where user can set like to news item.
        """
        total_likes = await like_news(
            session=request.app.db_session_factory,
            news_id=news_id,
            user_email=user_email,
        )
        return NewsLikeResponse(total_likes=total_likes)

    return router
