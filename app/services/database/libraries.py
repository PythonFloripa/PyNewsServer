from sqlmodel import SQLModel, Field

class Libraries(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    library_name: str
    user_email: str
    releases_url: str
    logo: str