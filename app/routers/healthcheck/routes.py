from fastapi import APIRouter, Request, status
from pydantic import BaseModel

from app.services.limiter import limiter


class HealthCheckResponse(BaseModel):
    status: str = "healthy"
    version: str = "2.0.0"


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
        """
        return HealthCheckResponse()

    return router
