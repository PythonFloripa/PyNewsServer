from fastapi import APIRouter

from app.routers.authentication import setup as authentication_router_setup
from app.routers.healthcheck.routes import setup as healthcheck_router_setup
from app.routers.libraries.routes import setup as libraries_router_setup
from app.routers.news.routes import setup as news_router_setup


def setup_router() -> APIRouter:
    router = APIRouter()
    router.include_router(healthcheck_router_setup(), prefix="")
    router.include_router(news_router_setup(), prefix="")
    router.include_router(authentication_router_setup(), prefix="")
    router.include_router(libraries_router_setup(), prefix="")
    return router
