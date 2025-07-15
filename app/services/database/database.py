from typing import Annotated

from fastapi import Depends #, FastAPI, HTTPException, Query
from sqlmodel import Field, SQLModel, create_engine ,Session, select




sqlite_file_path = "app/services/database/pynwesdb.db"
sqlite_url = f"sqlite:///{sqlite_file_path}"
# check_same_thread=False allows FastAPI to use the same SQLite database in different threads. This is necessary as one single request could use more than one thread.
connect_args = {"check_same_thread": False} 
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]