from sqlmodel import SQLModel, Field
from typing import Optional

class Community(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, nullable=False, unique=True)
    full_name: Optional[str] = None
    email: Optional[str] = None
    password: str  # senha hashed