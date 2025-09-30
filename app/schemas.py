from datetime import date
from typing import List

from pydantic import BaseModel

from app.enums import LibraryTagUpdatesEnum


class LibraryNews(BaseModel):
    tag: LibraryTagUpdatesEnum
    description: str


class Library(BaseModel):
    id: int | None = None
    library_name: str
    news: List[LibraryNews]
    logo: str
    version: str
    release_date: date
    releases_doc_url: str
    fixed_release_url: str
    language: str


class LibraryRequest(BaseModel):
    library_name: str
    library_home_page: str


# Community / User Class
class Community(BaseModel):
    username: str
    email: str


# Extends Community Class with hashed password
class CommunityInDB(Community):
    password: str


class News(BaseModel):
    title: str
    content: str
    category: str
    tags: str | None = None
    source_url: str
    social_media_url: str | None = None
    likes: int = 0


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    username: str


class Subscription(BaseModel):
    tags: List[LibraryTagUpdatesEnum]
    libraries_list: List[str]
