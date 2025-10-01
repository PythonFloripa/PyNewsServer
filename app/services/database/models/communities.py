from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class Community(SQLModel, table=True):
    __tablename__ = "communities"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str
    role: str = Field(default="user")
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
