from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class News(SQLModel, table=True):
    __tablename__ = "news"

    # Campos obrigatórios e suas definições
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    author: str
    category: str
    user_email: str
    source_url: str
    tags: str
    social_media_url: str
    likes: int = Field(default=0)

    # Chaves estrangeiras
    community_id: Optional[int] = Field(
            default=None,
            foreign_key="communities.id")
    # library_id: Optional[int]=Field(default=None, foreign_key="libraries.id")

    # Campos de data/hora
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now}
    )
