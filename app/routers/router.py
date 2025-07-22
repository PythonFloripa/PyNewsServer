from fastapi import APIRouter
from app.routers.healthcheck.routes import setup as healthcheck_router_setup
from app.routers.authentication import setup as authentication_router_setup


def setup_router() -> APIRouter:
    router = APIRouter()
    router.include_router(healthcheck_router_setup(), prefix='')
    router.include_router(authentication_router_setup(), prefix='')
    
    return router