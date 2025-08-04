from typing import Optional

from sqlmodel import SQLModel, Field


class Subscription(SQLModel, table=True):
    __tablename__ = 'subscriptions'

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str
    tags: str
    community_id: Optional[int] = Field(default=None, foreign_key="communities.id")
