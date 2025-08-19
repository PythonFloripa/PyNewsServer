from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from services.database.orm.library import get_library_ids_by_multiple_names
from services.database.orm.subscription import create_multiple_subscription

from app.schemas import Subscription as SubscriptionSchema
from app.services.database.models import Subscription


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
    async def subscribe_libraries(
        request: Request,
        body: SubscriptionSchema,
    ):
        library_ids = await get_library_ids_by_multiple_names(
            body.libraries_list, request.app.db_session_factory
        )

        subscriptions = [
            Subscription(email=body.email, tags=body.tags, library_id=id)
            for id in library_ids
        ]

        await create_multiple_subscription(
            subscriptions,
            request.app.db_session_factory,
        )

        return SubscribeLibraryResponse()

    return router
