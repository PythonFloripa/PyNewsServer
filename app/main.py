import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI , Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.database import init_db, get_session, TestEntry, AsyncSessionLocal
from app.routers.router import setup_router as setup_router_v2


logger = logging.getLogger(__name__) 


@asynccontextmanager
async def lifespan(app: FastAPI):
    ## add check db file and create if not found 
    await init_db() 
    app.db_session_factory = AsyncSessionLocal
    try:
        yield
    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    title='pynews-server',
    description='PyNews Server',
)

async def get_db_session():
    # Usa app.attr para acessar a fábrica de sessões que foi injetada
    async with app.db_session_factory() as session: 
        yield session

app.include_router(setup_router_v2(), prefix='/api')

logger.info('PyNews Server Starter')
