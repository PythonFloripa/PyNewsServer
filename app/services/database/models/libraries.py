from typing import Optional

from sqlmodel import Field, SQLModel


class Library(SQLModel, table=True):
    __tablename__ = "libraries"

    id: Optional[int] = Field(default=None, primary_key=True)
    library_name: str
    email: str
    releases_url: str
    logo: str
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
