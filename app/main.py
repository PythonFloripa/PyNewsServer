import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI , Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from httpx import AsyncClient
from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.database import init_db, get_session, TestEntry, AsyncSessionLocal
from app.routers.router import setup_router as setup_router_v2


logger = logging.getLogger(__name__) 


@asynccontextmanager
async def lifespan(app: FastAPI):
    ## add check db file and create if not found 
    await init_db() 
    app.db_session_factory = AsyncSessionLocal ## setup do objeto para
    try:
        yield
    finally:
        pass


app = FastAPI(
    lifespan=lifespan,
    title='pynews-server',
    description='PyNews Server',
)

async def get_db_session():
    # Usa app.attr para acessar a fábrica de sessões que foi injetada
    async with app.db_session_factory() as session: 
        yield session

app.include_router(setup_router_v2(), prefix='/api')

logger.info('PyNews Server Starter')



"""  
Testes enquanto a implementação dos modelos finais do projeto não estão nos arquivos.
"""

@app.post("/test-entry/", response_model=TestEntry)
async def create_entry(message: str, session: AsyncSession = Depends(get_db_session)):
    """
    Cria uma nova entrada de teste no banco de dados.
    """
    new_entry = TestEntry(message=message)
    session.add(new_entry)
    await session.commit()
    await session.refresh(new_entry)
    return new_entry

@app.get("/test-entries/", response_model=List[TestEntry])
async def read_entries(session: AsyncSession = Depends(get_db_session)):
    """
    Retorna todas as entradas de teste do banco de dados.
    """
    from sqlmodel import select # Importa select para consultas
    result = await session.exec(select(TestEntry)) 
    return result.all()