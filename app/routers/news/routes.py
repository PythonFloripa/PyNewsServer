from fastapi import APIRouter, status
from pydantic import BaseModel


class NewsPostResponse(BaseModel):
    status: str = "News Criada"


def setup():
    router = APIRouter(prefix="/news", tags=["news"])

    @router.post(
        "",
        response_model=NewsPostResponse,
        status_code=status.HTTP_200_OK,
        summary="News endpoint",
        description="Creates news and returns a confirmation message",
    )
    async def news():
        """
        News endpoint that creates news and returns a confirmation message.
        """
        return NewsPostResponse()

    return router
