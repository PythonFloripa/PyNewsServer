from datetime import UTC, datetime
from typing import Sequence, Tuple
from unittest.mock import AsyncMock

import pytest
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

import app.main as main_app
import app.services.email_jobs as email_jobs
from app.services.database.models.subscriptions import Subscription
from app.services.email_jobs import send_daily_subscriptions_email
from tests.conftest import TestSessionLocal


@pytest.fixture(autouse=True)
def patch_async_session_local(monkeypatch):
    monkeypatch.setattr(email_jobs, "AsyncSessionLocal", TestSessionLocal)


@pytest.mark.asyncio
async def test_send_daily_subscriptions_email_sends_unique_recipients(
    session: AsyncSession, monkeypatch
):
    sent_payloads: list[Tuple[Sequence[str], str, str]] = []

    def fake_send_bulk_emails(
        recipients: Sequence[str], subject: str, body: str
    ) -> None:
        sent_payloads.append((list(recipients), subject, body))

    monkeypatch.setattr(email_jobs, "send_bulk_emails", fake_send_bulk_emails)
    monkeypatch.setenv("DAILY_SUBSCRIPTION_EMAIL_SUBJECT", "Daily Digest")
    monkeypatch.setenv(
        "DAILY_SUBSCRIPTION_EMAIL_BODY", "<p>Custom body content</p>"
    )

    session.add_all(
        [
            Subscription(user_email="alice@example.com", tags=[]),
            Subscription(
                user_email="bob@example.com",
                tags=[],
            ),
            Subscription(user_email="alice@example.com", tags=[]),
        ]
    )
    await session.commit()

    expected_date = datetime.now(tz=UTC).strftime("%d/%m/%Y")

    await send_daily_subscriptions_email()

    assert len(sent_payloads) == 1
    recipients, subject, body = sent_payloads[0]
    assert set(recipients) == {"alice@example.com", "bob@example.com"}
    assert subject == f"Daily Digest - {expected_date}"
    assert body == "<p>Custom body content</p>"


@pytest.mark.asyncio
async def test_send_daily_subscriptions_email_skips_without_recipients(
    monkeypatch,
):
    def fail_send_bulk_emails(*args, **kwargs):
        raise AssertionError("Should not be called")

    monkeypatch.setattr(email_jobs, "send_bulk_emails", fail_send_bulk_emails)

    await send_daily_subscriptions_email()


@pytest.mark.asyncio
async def test_lifespan_registers_daily_email_job(monkeypatch):
    async def fake_init_db():
        return None

    async def fake_create_admin(session):
        return None

    monkeypatch.setattr(main_app, "init_db", fake_init_db)
    monkeypatch.setattr(
        main_app, "create_admin", AsyncMock(side_effect=fake_create_admin)
    )
    monkeypatch.setattr(main_app, "AsyncSessionLocal", lambda: "session")
    monkeypatch.setattr(
        main_app, "send_daily_subscriptions_email", AsyncMock()
    )

    previous_session_factory = getattr(
        main_app.app, "db_session_factory", None
    )
    previous_scheduler = getattr(main_app.app.state, "scheduler", None)

    async with main_app.lifespan(main_app.app):
        scheduler = main_app.app.state.scheduler
        assert scheduler.running

        job = scheduler.get_job("daily_subscription_email_job")
        assert job is not None
        assert isinstance(job.trigger, CronTrigger)
        assert job.next_run_time is not None
        assert job.next_run_time.hour == 3
        assert job.next_run_time.minute == 0

    if previous_session_factory is not None:
        main_app.app.db_session_factory = previous_session_factory
    elif hasattr(main_app.app, "db_session_factory"):
        delattr(main_app.app, "db_session_factory")

    if previous_scheduler is not None:
        main_app.app.state.scheduler = previous_scheduler
    elif hasattr(main_app.app.state, "scheduler"):
        delattr(main_app.app.state, "scheduler")

