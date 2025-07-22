from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Library(SQLModel, table=True):
    __tablename__ = "libraries"

    id: Optional[int] = Field(default=None, primary_key=True)
    library_name: str
    user_email: str
    releases_url: str
    logo: str
    community_id: Optional[int] = Field(default=None, foreign_key="communities.id")