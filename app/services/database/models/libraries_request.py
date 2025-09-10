from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class LibraryRequest(SQLModel, table=True):
    __tablename__ = "libraries_request"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_email: str
    library_name: str
    library_home_page: str
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
