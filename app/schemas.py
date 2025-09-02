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
class SubscriptionTagEnum(str, Enum):
    UPDATE = "update"
    BUG_FIX = "bug_fix"
    NEW_FEATURE = "new_feature"
    SECURITY_FIX = "security_fix"


class Subscription(BaseModel):
    email: str
    tags: List[SubscriptionTagEnum]
    libraries_list: List[str]
