from enum import Enum
from typing import List

from pydantic import BaseModel, HttpUrl


class Library(BaseModel):
    library_name: str
    releases_url: HttpUrl
    logo: HttpUrl


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


# Subscription Class
class TagEnum(str, Enum):
    bug_fix = "bug_fix"
    update = "update"
    deprecate = "deprecate"
    new_feature = "new_feature"
    security_fix = "security_fix"


class Subscription(BaseModel):
    tags: List[TagEnum]
    libraries_list: List[str]
