from typing import Optional

from sqlmodel import SQLModel, Field

class Community(SQLModel, table=True):
    __tablename__ = "communities"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str