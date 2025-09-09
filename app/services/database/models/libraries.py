from datetime import date
from typing import Optional

from sqlmodel import Field, SQLModel


class Library(SQLModel, table=True):
    __tablename__ = "libraries"

    id: Optional[int] = Field(default=None, primary_key=True)
    library_name: str
    user_email: str
    logo: str
    version: str
    release_date: date
    releases_doc_url: str
    fixed_release_url: str
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
