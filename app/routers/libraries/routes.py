from typing import Annotated, List

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.params import Depends
from pydantic import BaseModel

from app.routers.authentication import get_current_active_community
from app.schemas import Library as LibrarySchema
from app.schemas import LibraryNews
from app.schemas import LibraryRequest as LibraryRequestSchema
from app.schemas import Subscription as SubscriptionSchema
from app.services.database.models import Library, Subscription
from app.services.database.models.communities import Community as DBCommunity
from app.services.database.models.libraries_request import LibraryRequest
from app.services.database.orm.library import (
    get_libraries_by_language,
    get_library_ids_by_multiple_names,
    insert_library,
)
from app.services.database.orm.library_request import insert_library_request
from app.services.database.orm.subscription import upsert_multiple_subscription
from app.services.encryption import encrypt_email
from app.services.limiter import limiter


class LibraryResponse(BaseModel):
    status: str = "Library created successfully"


class SubscribeLibraryResponse(BaseModel):
    status: str = "Subscribed in libraries successfully"


class LibraryRequestResponse(BaseModel):
    status: str = "Library requested successfully"


def setup():
    router = APIRouter(prefix="/libraries", tags=["libraries"])

    @router.get(
        "",
        response_model=List[LibrarySchema],
        status_code=status.HTTP_200_OK,
        summary="Get libraries by language",
        description="Get libraries by language",
    )
    @limiter.limit("60/minute")
    async def get_by_language(
        request: Request,
        language: str,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
    ):
        try:
            libraryList = await get_libraries_by_language(
                language=language, session=request.app.db_session_factory
            )
            return [
                LibrarySchema(
                    library_name=libraryDb.library_name,
                    news=[
                        LibraryNews(
                            tag=news["tag"], description=news["description"]
                        )
                        for news in libraryDb.news
                    ],
                    logo=libraryDb.logo,
                    version=libraryDb.version,
                    release_date=libraryDb.release_date,
                    releases_doc_url=libraryDb.releases_doc_url,
                    fixed_release_url=libraryDb.fixed_release_url,
                    language=libraryDb.language,
                )
                for libraryDb in libraryList
            ]
        except HTTPException as e:
            raise e
        except Exception as e:
            HTTPException(status_code=500, detail=f"Unexpected error: {e}")

    @router.post(
        "",
        response_model=LibraryResponse,
        status_code=status.HTTP_200_OK,
        summary="Create a library",
        description="Create a new library to follow",
    )
    @limiter.limit("60/minute")
    async def create_library(
        request: Request,
        body: LibrarySchema,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
    ):
        library = Library(
            library_name=body.library_name,
            news=[news.model_dump() for news in body.news],
            logo=body.logo,
            version=body.version,
            release_date=body.release_date,
            releases_doc_url=body.releases_doc_url,
            fixed_release_url=body.fixed_release_url,
            language=body.language,
            community_id=current_community.id,
        )
        try:
            await insert_library(library, request.app.db_session_factory)
            return LibraryResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {e}"
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
    @limiter.limit("60/minute")
    async def subscribe_libraries(
        request: Request,
        body: SubscriptionSchema,
        user_email: Annotated[str, Header(alias="user-email")],
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
    ):
        try:
            library_ids = await get_library_ids_by_multiple_names(
                body.libraries_list, request.app.db_session_factory
            )

            if (library_ids is None) or (len(library_ids) == 0):
                raise HTTPException(
                    status_code=404, detail="Libraries not found"
                )

            subscriptions = [
                Subscription(
                    user_email=encrypt_email(user_email),
                    tags=body.tags,
                    library_id=id,
                    community_id=current_community.id,
                )
                for id in library_ids
            ]

            await upsert_multiple_subscription(
                subscriptions, request.app.db_session_factory
            )

            return SubscribeLibraryResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {e}"
            )

    @router.post(
        "/request",
        response_model=LibraryRequestResponse,
        status_code=status.HTTP_200_OK,
        summary="Request a library",
        description="Request a library to follow",
    )
    @limiter.limit("60/minute")
    async def request_library(
        request: Request,
        body: LibraryRequestSchema,
        user_email: Annotated[str, Header(alias="user-email")],
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
    ):
        try:
            library_request = LibraryRequest(
                user_email=user_email,
                library_name=body.library_name,
                library_home_page=body.library_home_page,
                community_id=current_community.id,
            )

            await insert_library_request(
                library_request, request.app.db_session_factory
            )

            return LibraryRequestResponse()
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Unexpected error: {e}"
            )

    return router
