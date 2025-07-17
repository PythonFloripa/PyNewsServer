import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient


from app.routers.router import setup_router as setup_router_v2


logger = logging.getLogger(__name__) 


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        yield
    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    title='pynews-server',
    description='PyNews Server',
)

app.include_router(setup_router_v2(), prefix='/api')

logger.info('PyNews Server Starter')
