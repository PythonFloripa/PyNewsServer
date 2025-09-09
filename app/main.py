import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler

from app.routers.router import setup_router as setup_router_v2
from app.services.database.database import AsyncSessionLocal, init_db
from app.services.limiter import limiter

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # add check db file and create if not found
    await init_db()
    app.db_session_factory = AsyncSessionLocal()
    try:
        yield
    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    title="pynews-server",
    description="PyNews Server",
)


app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.include_router(setup_router_v2(), prefix="/api")

logger.info("PyNews Server Starter")
