from typing import List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel

from app.schemas import SubscriptionTagEnum


class Subscription(SQLModel, table=True):
    __tablename__ = "subscriptions"  # type: ignore

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    tags: List[SubscriptionTagEnum] = Field(sa_column=Column(JSON))
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
    library_id: Optional[int] = Field(default=None, foreign_key="libraries.id")
