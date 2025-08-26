from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.schemas import Library as LibrarySchema
from app.services.database.models.libraries import Library
from app.services.database.orm.library import insert_library


class LibraryResponse(BaseModel):
    status: str = "Library created successfully"


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
        await insert_library(
            Library(
                library_name=body.library_name,
                user_email="",
                releases_url=body.releases_url.encoded_string(),
                logo=body.logo.encoded_string(),
            ),
            request.app.db_session_factory,
        )

        return LibraryResponse()

    return router
