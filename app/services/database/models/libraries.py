from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, SQLModel


class Library(SQLModel, table=True):
    __tablename__ = "libraries"

    id: Optional[int] = Field(default=None, primary_key=True)
    library_name: str
    news: List[dict] = Field(sa_column=Column(JSON))
    logo: str
    version: str
    release_date: date
    releases_doc_url: str
    fixed_release_url: str
    language: str
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
