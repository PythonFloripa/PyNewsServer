from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import List
from enum import Enum


# Subscription
class TagEnum(str, Enum):
    bug_fix = "bug_fix"
    update = "update"
    deprecate = "deprecate"
    new_feature = "new_feature"
    security_fix = "security_fix"

class Subscription(BaseModel):
    tags: List[TagEnum]
    libraries_list: List[str]

# News
class News(BaseModel):
    description: str
    tag: str

class Library(BaseModel):
    library_name: str
    news: list[News]
    logo: HttpUrl
    version: str
    release_date: datetime
    release_doc_url: HttpUrl