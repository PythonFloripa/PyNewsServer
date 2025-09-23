from typing import Dict, List, Tuple

from sqlalchemy import tuple_
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models.subscriptions import Subscription


async def upsert_multiple_subscription(
    subscriptions: List[Subscription],
    session: AsyncSession,
) -> List[Subscription]:
    if not subscriptions:
        return []

    incoming_map: Dict[Tuple[str, int | None], Subscription] = {
        (sub.user_email, sub.library_id): sub for sub in subscriptions
    }

    keys_to_check = incoming_map.keys()
    stmt = select(Subscription).where(
        tuple_(Subscription.user_email, Subscription.library_id).in_(
            keys_to_check
        )
    )

    result = await session.exec(stmt)
    existing_subscriptions = result.all()
    existing_map: Dict[Tuple[str, int | None], Subscription] = {
        (sub.user_email, sub.library_id): sub for sub in existing_subscriptions
    }

    new_subscriptions: List[Subscription] = []
    for key, sub_to_upsert in incoming_map.items():
        if existing_sub := existing_map.get(key):
            existing_sub.tags = sub_to_upsert.tags
        else:
            new_subscriptions.append(sub_to_upsert)

    session.add_all(new_subscriptions)
    await session.commit()

    all_subs = list(existing_subscriptions) + new_subscriptions

    for sub in all_subs:
        await session.refresh(sub)

    return all_subs
