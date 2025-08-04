from datetime import datetime

from pydantic import BaseModel, HttpUrl


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
