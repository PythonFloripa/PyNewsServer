from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from app.schemas import Library as LibrarySchema
from app.schemas import Subscription as SubscriptionSchema
from app.services.database.models import Library, Subscription
from app.services.database.orm.library import (
    get_library_ids_by_multiple_names,
    insert_library,
)
from app.services.database.orm.subscription import upsert_multiple_subscription


class LibraryResponse(BaseModel):
    status: str = "Library created successfully"


class SubscribeLibraryResponse(BaseModel):
    status: str = "Subscribed in libraries successfully"


def setup():
    router = APIRouter(prefix="/libraries", tags=["libraries"])

    @router.post(
        "",
        response_model=LibraryResponse,
        status_code=status.HTTP_200_OK,
        summary="Create a library",
        description="Create a new library to follow",
    )
    async def create_library(
        request: Request,
        body: LibrarySchema,
    ):
        library = Library(
            library_name=body.library_name,
            user_email="",  # TODO: Considerar obter o email do usuário autenticado
            logo=body.logo.encoded_string(),
            version=body.version,
            release_date=body.release_date,
            releases_doc_url=body.releases_doc_url.encoded_string(),
            fixed_release_url=body.fixed_release_url.encoded_string(),
        )
        try:
            await insert_library(library, request.app.db_session_factory)
            return LibraryResponse()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to create library: {e}"
            )

    @router.post(
        "/subscribe",
        response_model=SubscribeLibraryResponse,
        status_code=status.HTTP_200_OK,
        summary="Subscribe to receive library updates",
        description=(
            "Subscribe to multiple libs and tags to receive libs updates"
        ),
    )
    async def subscribe_libraries(
        request: Request,
        body: SubscriptionSchema,
    ):
        try:
            library_ids = await get_library_ids_by_multiple_names(
                body.libraries_list, request.app.db_session_factory
            )

            subscriptions = [
                Subscription(email=body.email, tags=body.tags, library_id=id)
                for id in library_ids
            ]

            await upsert_multiple_subscription(
                subscriptions, request.app.db_session_factory
            )

            return SubscribeLibraryResponse()
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Subscription failed: {e}"
            )

    return router
