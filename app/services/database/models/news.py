from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class News(SQLModel, table=True):
    """
    Represents a news article in the database.

    Attributes:
        id (Optional[int]): Unique identifier for the news article.
            Auto-generated primary key.
        title (str): The headline or title of the news article.
        content (str): The main body or text content of the news.
        category (str): Category or topic classification
            (e.g., "Politics", "Tech").
        user_email (str): Email of the user who submitted or is associated
            with this news.
        source_url (str): URL pointing to the original source of the news.
        tags (str): Comma-separated or JSON-encoded string of tags for
            search/filtering.
        user_email_list (str): encoded list of emails of users who liked
            this news. Defaults to an empty list.
        social_media_url (str): URL to the social media post or share link
            for this news.
        likes (int): Number of likes this news article has received.
            Defaults to 0.

        community_id (Optional[int]): Foreign key to the associated community
            (communities.id).

        created_at (Optional[datetime]): Timestamp when the news was first
            created. Defaults to now.
        updated_at (Optional[datetime]): Timestamp when the news was last
            updated. Auto-updates on modification.
    """

    __tablename__ = "news"

    # Campos obrigatórios e suas definições
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    content: str
    category: str
    user_email: str
    source_url: str
    tags: str
    user_email_list: str = Field(default="[]")
    social_media_url: str
    likes: int = Field(default=0)

    # Chaves estrangeiras
    community_id: Optional[int] = Field(
        default=None, foreign_key="communities.id"
    )
    # library_id: Optional[int]=Field(default=None, foreign_key="libraries.id")

    # Campos de data/hora
    created_at: Optional[datetime] = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = Field(
        default_factory=datetime.now,
        sa_column_kwargs={"onupdate": datetime.now},
    )
