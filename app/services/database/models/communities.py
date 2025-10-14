from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String
from sqlmodel import Field, SQLModel


class Community(SQLModel, table=True):
    __tablename__ = "communities"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str = Field(
        sa_column=Column("email", String, unique=True)
    )  # VARCHAR(255), unique key
    password: str
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
    role: str = Field(default="user")  # user or admin
