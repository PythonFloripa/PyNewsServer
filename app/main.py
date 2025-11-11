import logging
import os
from contextlib import asynccontextmanager
from datetime import UTC
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler

from app.routers.admin.routes import create_admin
from app.routers.router import setup_router as setup_router_v2
from app.services.database.database import AsyncSessionLocal, init_db
from app.services.email_jobs import send_daily_subscriptions_email
from app.services.limiter import limiter

logger = logging.getLogger(__name__)


def _resolve_timezone():
    tz_name = os.getenv("APP_TIMEZONE")
    if not tz_name:
        return UTC

    try:
        return ZoneInfo(tz_name)
    except ZoneInfoNotFoundError:
        logger.warning(
            "Fuso horário '%s' inválido. Revertendo para UTC.", tz_name
        )
        return UTC


@asynccontextmanager
async def lifespan(app: FastAPI):
    # add check db file and create if not found
    await init_db()
    app.db_session_factory = AsyncSessionLocal()
    scheduler = AsyncIOScheduler(timezone=_resolve_timezone())
    scheduler.add_job(
        send_daily_subscriptions_email,
        CronTrigger(hour=3, minute=0),
        id="daily_subscription_email_job",
        name="Disparo diário de e-mails para assinantes",
        replace_existing=True,
    )
    scheduler.start()
    app.state.scheduler = scheduler
    await create_admin(app.db_session_factory)
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(
    lifespan=lifespan,
    title="pynews-server",
    description="PyNews Server",
)


app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)

app.include_router(setup_router_v2(), prefix="/api")

logger.info("PyNews Server Starter")
