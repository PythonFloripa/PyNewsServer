import logging
import os
from datetime import UTC, datetime
from typing import Iterable

from app.services.database.database import AsyncSessionLocal
from app.services.database.orm.subscription import get_subscription_emails
from app.services.email_sender import send_bulk_emails

logger = logging.getLogger(__name__)


async def _load_recipients() -> Iterable[str]:
    async with AsyncSessionLocal() as session:
        return await get_subscription_emails(session)


async def send_daily_subscriptions_email() -> None:
    recipients = await _load_recipients()
    recipient_list = [
        email for email in recipients if email and email.strip()
    ]

    if not recipient_list:
        logger.info(
            "Nenhum destinatário encontrado para o disparo diário "
            "de assinantes."
        )
        return

    subject = os.getenv("DAILY_SUBSCRIPTION_EMAIL_SUBJECT", "PyNews Daily")
    today = datetime.now(tz=UTC).strftime("%d/%m/%Y")
    default_body = (
        "<p>Confira as novidades mais recentes da comunidade PyNews.</p>"
    )
    body = os.getenv("DAILY_SUBSCRIPTION_EMAIL_BODY", default_body)

    logger.info(
        "Iniciando envio de e-mails diário para %s destinatários em %s.",
        len(recipient_list),
        today,
    )

    send_bulk_emails(
        recipients=recipient_list,
        subject=f"{subject} - {today}",
        body=body,
    )


