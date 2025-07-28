import logging
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, Field
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database import models

logger = logging.getLogger(__name__)

# --- Configuração do Banco de Dados ---
# 'sqlite+aiosqlite' para suporte assíncrono com SQLite
SQLITE_PATH = os.getenv('SQLITE_PATH', 'pynewsdb.db') # Valor padrão se não definida
SQLITE_URL = os.getenv('SQLITE_URL', f'sqlite+aiosqlite:///{SQLITE_PATH}')

DATABASE_FILE = SQLITE_PATH # Usamos SQLITE_PATH para o nome do arquivo
DATABASE_URL = SQLITE_URL # Usamos SQLITE_URL para a URL completa

# Cria o motor assíncrono 
engine: AsyncEngine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

# --- Fábrica de Sessões Assíncronas ---
# Crie a fábrica de sessões UMA VEZ no escopo global do módulo.
# Esta é a variável é injetada para obter sessões nas chamadas. 
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, echo= True # expire_on_commit=False é importante!
)

# --- Modelo de Teste Temporário (SQLModel) ---
class TestEntry(SQLModel, table=True): # table=True indica que esta classe é um modelo de tabela
    """
    Classe de modelo temporária para testes de conexão com o banco de dados.
    Será usada como uma solução provisória antes da implementação dos modelos finais do projeto.
    """
    __tablename__ = "test_entries"
    id: int | None = Field(default=None, primary_key=True)
    message: str

    def __repr__(self):
        return f"<TestEntry(id={self.id}, message='{self.message}')>"
    

# --- Funções de Inicialização e Sessão do Banco de Dados ---
async def init_db():
    """
    Inicializa o banco de dados:
    1. Verifica se o arquivo do banco de dados existe.
    2. Se não existir, cria o arquivo e todas as tabelas definidas nos modelos SQLModel nos imports e acima.
    """
    if not os.path.exists(DATABASE_FILE):
        logger.info(f"Arquivo de banco de dados '{DATABASE_FILE}' não encontrado. Criando novo banco de dados e tabelas.")
        async with engine.begin() as conn:
            # SQLModel.metadata.create_all é síncrono e precisa ser executado via run_sync
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Tabelas criadas com sucesso.")
    else:
        logger.info(f"Arquivo de banco de dados '{DATABASE_FILE}' já existe. Conectando.")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Função utilitária que fornece uma sessão de banco de dados assíncrona.
    Injeção de dependência no app no lifespan. 
    """
    async with AsyncSessionLocal() as session:
        yield session
    # chamada do session.close() acontece ao final do bloco async with(). 
