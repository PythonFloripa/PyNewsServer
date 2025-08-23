from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from services.database.orm.news import get_news_by_query_params


class NewsPostResponse(BaseModel):
    status: str = "News Criada"


class NewsGetResponse(BaseModel):
    status: str = "Lista de News Obtida"
    news_list: list = []


def setup():
    router = APIRouter(prefix="/news", tags=["news"])

    @router.post(
        "",
        response_model=NewsPostResponse,
        status_code=status.HTTP_200_OK,
        summary="News endpoint",
        description="Creates news and returns a confirmation message",
    )
    async def post_news():
        """
        News endpoint that creates news and returns a confirmation message.
        """
        return NewsPostResponse()

    @router.get(
        "",
        response_model=NewsGetResponse,
        status_code=status.HTTP_200_OK,
        summary="Get News",
        description="Retrieves news filtered by user and query params",
    )
    async def get_news(request: Request):
        """
        Get News endpoint that retrieves news filtered by user and query params.
        """
        news_list = await get_news_by_query_params(
            session=request.app.db_session_factory,
            id=request.query_params.get("id"),
            user_email=request.headers.get("user-email"),
            category=request.query_params.get("category"),
            tags=request.query_params.get("tags"),
        )
        return NewsGetResponse(news_list=news_list)

    return router
