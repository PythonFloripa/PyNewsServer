from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.services.database.database import get_session
from app.services.limiter import limiter


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"
    database: str = "connected"


def setup():
    router = APIRouter(prefix="/healthcheck", tags=["healthcheck"])

    @router.get(
        "",
        response_model=HealthCheckResponse,
        status_code=status.HTTP_200_OK,
        summary="Health check endpoint",
        description="Returns the health status of the API",
    )
    @limiter.limit("60/minute")
    async def healthcheck(request: Request):
        """
        Health check endpoint that returns the current status of the API.
        Includes database connectivity check.
        """
        database_status = "connected"

        try:
            # Test database connection by getting a session
            async for _ in get_session():
                # If we can get a session, the database is connected
                break
        except Exception:
            database_status = "disconnected"

        return HealthCheckResponse(database=database_status)

    return router
