from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models.subscriptions import Subscription


async def create_multiple_subscription(
    subscriptions: List[Subscription],
    session: AsyncSession,
):
    session.add_all(subscriptions)
    await session.commit()
    await session.refresh(subscriptions)
