from fastapi import APIRouter, status
from pydantic import BaseModel


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
    async def healthcheck():
        """
        Health check endpoint that returns the current status of the API.
        """
        return HealthCheckResponse()

    return router
