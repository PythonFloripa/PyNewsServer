from sqlmodel import SQLModel, Field

class Communities(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str
    email: str
    password: str