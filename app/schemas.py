from datetime import date
from enum import Enum
from typing import List

from pydantic import BaseModel, HttpUrl


class LibraryTagEnum(str, Enum):
    UPDATES = "updates"
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    SECURITY_FIX = "security_fix"
    DEPRECATION = "deprecation"


class LibraryNews(BaseModel):
    tag: LibraryTagEnum
    description: str


class Library(BaseModel):
    library_name: str
    news: List[LibraryNews]
    logo: HttpUrl
    version: str
    release_date: date
    releases_doc_url: HttpUrl
    fixed_release_url: HttpUrl


# Community / User Class
class Community(BaseModel):
    username: str
    email: str


# Extends Community Class with hashed password
class CommunityInDB(Community):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


class TokenPayload(BaseModel):
    username: str


class Subscription(BaseModel):
    email: str
    tags: List[LibraryTagEnum]
    libraries_list: List[str]
