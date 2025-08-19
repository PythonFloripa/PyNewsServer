from fastapi import APIRouter, status
from pydantic import BaseModel


class SubscribeLibraryResponse(BaseModel):
    status: str = "Subscribed in libraries successfully"


def setup():
    router = APIRouter(prefix="/libraries", tags=["libraries"])

    @router.get(
        "/subscribe",
        response_model=SubscribeLibraryResponse,
        status_code=status.HTTP_200_OK,
        summary="Subscribe to receive library updates",
        description="Subscribe to multiple libs and tags to receive libs updates",
    )
    async def subscribe_libraries():
        
        return SubscribeLibraryResponse()


    return router
