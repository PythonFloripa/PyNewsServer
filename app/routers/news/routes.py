import os
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, Request, status
from fastapi.params import Header
from pydantic import BaseModel

import app.services.database.orm.news as orm_news
from app.routers.authentication import get_current_active_community
from app.schemas import News, NewsPublishStatus
from app.services.database.models import Community as DBCommunity
from app.services.limiter import limiter

SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


class NewsCreateResponse(BaseModel):
    status: str = "News Criada"


class NewsGetResponse(BaseModel):
    status: str = "Lista de News Obtida"
    news_list: list = []


class NewsUpdateResponse(BaseModel):
    status: str = "News Atualizada"


class NewsLikeResponse(BaseModel):
    total_likes: int | None


def encode_email(email: str) -> str:
    """Encodes the email to be safely stored in database."""
    return jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)


def setup():
    router = APIRouter(prefix="/news", tags=["news"])

    @router.post(
        "",
        response_model=NewsCreateResponse,
        status_code=status.HTTP_200_OK,
        summary="News endpoint",
        description="Creates news and returns a confirmation message",
    )
    @limiter.limit("60/minute")
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
        await orm_news.create_news(
            session=request.app.db_session_factory, news=news_dict
        )
        return NewsCreateResponse()

    @router.get(
        "",
        response_model=NewsGetResponse,
        status_code=status.HTTP_200_OK,
        summary="Get News",
        description="Retrieves news filtered by user and query params",
    )
    @limiter.limit("60/minute")
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
        news_list = await orm_news.get_news_by_query_params(
            session=request.app.db_session_factory,
            id=id,
            email=user_email,
            category=category,
            tags=tags,
        )
        return NewsGetResponse(news_list=news_list)

    @router.put(
        "",
        response_model=NewsGetResponse,
        status_code=status.HTTP_200_OK,
        summary="PUT News",
        description="Updates news by query params and set publish value",
    )
    @limiter.limit("60/minute")
    async def put_news(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        publish_status: NewsPublishStatus,
        id: str | None = None,
        title: str | None = None,
        content: str | None = None,
        category: str | None = None,
        user_email: str = str(Header(..., alias="user-email")),
        source_url: str | None = None,
        tags: str | None = None,
        social_media_url: str | None = None,
    ):
        """
        Get News endpoint that retrieves news filtered by user and query params.
        """
        news: dict = {
            "id": id,
            "title": title,
            "content": content,
            "category": category,
            "user_email": user_email,
            "source_url": source_url,
            "tags": tags,
            "social_media_url": social_media_url,
            "publish": publish_status.publish,
        }
        await orm_news.update_news(
            session=request.app.db_session_factory, news=news
        )
        return NewsUpdateResponse()

    @router.post(
        path="/{news_id}/like",
        response_model=NewsLikeResponse,
        status_code=status.HTTP_200_OK,
        summary="News like endpoint",
        description="Allows user to like a news item",
    )
    @limiter.limit("60/minute")
    async def post_like(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        news_id: str,
        user_email: str = Header(..., alias="user-email"),
    ):
        """
        News endpoint where user can set like to news item.
        """
        encoded_email = encode_email(user_email)
        total_likes = await orm_news.like_news(
            session=request.app.db_session_factory,
            news_id=news_id,
            email=encoded_email,
        )
        return NewsLikeResponse(total_likes=total_likes)

    @router.delete(
        path="/{news_id}/like",
        response_model=NewsLikeResponse,
        status_code=status.HTTP_200_OK,
        summary="News undo like endpoint",
        description="Allows user to undo a like to a news item",
    )
    @limiter.limit("60/minute")
    async def delete_like(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
        news_id: str,
        user_email: str = Header(..., alias="user-email"),
    ):
        """
        News endpoint where user can set like to news item.
        """
        encoded_email = encode_email(user_email)
        total_likes = await orm_news.delete_like(
            session=request.app.db_session_factory,
            news_id=news_id,
            email=encoded_email,
        )
        return NewsLikeResponse(total_likes=total_likes)

    return router
