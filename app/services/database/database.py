import logging
import os
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlmodel import Field, SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database import models  # noqa F401
from app.services.database.models import (  # noqa F401
    Community,
    Library,
    LibraryRequest,
    News,
    Subscription,
)

logger = logging.getLogger(__name__)


# --- Configuração do Banco de Dados ---
# 'sqlite+aiosqlite' para suporte assíncrono com SQLite
SQLITE_PATH = os.getenv(
    "SQLITE_PATH", "pynewsdb.db"
)  # Valor padrão se não definida
SQLITE_URL = os.getenv("SQLITE_URL", f"sqlite+aiosqlite:///{SQLITE_PATH}")

DATABASE_FILE = SQLITE_PATH  # Usamos SQLITE_PATH para o nome do arquivo
DATABASE_URL = SQLITE_URL  # Usamos SQLITE_URL para a URL completa

# Cria o motor assíncrono
engine = create_async_engine(DATABASE_URL, echo=True, future=True)


# --- Fábrica de Sessões Assíncronas ---
# Crie a fábrica de sessões UMA VEZ no escopo global do módulo.
# Esta é a variável é injetada para obter sessões nas chamadas.
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    # echo=True,  # expire_on_commit=False é importante!
)


# --- Modelo de Teste Temporário (SQLModel) ---
class TestEntry(
    SQLModel, table=True
):  # table=True indica que esta classe é um modelo de tabela
    """
    Classe de modelo temporária para testes de conexão com o banco de dados.
    Será usada como uma solução provisória antes da implementação dos
    modelos finais do projeto.
    """

    id: int | None = Field(default=None, primary_key=True)
    message: str
    __tablename__ = "test_entry"

    def __repr__(self):
        return f"<TestEntry(id={self.id}, message='{self.message}')>"


# --- Funções de Inicialização e Sessão do Banco de Dados ---
async def init_db():
    """
    Inicializa o banco de dados:
    1. Verifica se o arquivo do banco de dados existe.
    2. Conecta ao banco e verifica se as tabelas existem.
    3. Cria tabelas faltantes se necessário.
    """
    try:
        # Cria o diretório do banco se não existir
        db_dir = os.path.dirname(DATABASE_FILE)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            logger.info(f"Diretório criado: {db_dir}")

        # Verifica se o arquivo existe
        db_exists = os.path.exists(DATABASE_FILE)

        if not db_exists:
            logger.info(
                f"Arquivo de banco de dados '{DATABASE_FILE}' não encontrado. "
                f"Criando novo banco de dados."
            )
        else:
            logger.info(f"Conectando ao banco de dados '{DATABASE_FILE}'.")

        # Sempre tenta criar as tabelas (create_all é idempotente)
        # Se as tabelas já existem, o SQLModel não fará nada
        async with engine.begin() as conn:
            # SQLModel.metadata.create_all é síncrono e precisa
            # ser executado via run_sync
            await conn.run_sync(SQLModel.metadata.create_all)

        # Verifica quais tabelas foram criadas/existem
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                text(
                    "SELECT name FROM sqlite_master WHERE type='table' "
                    "ORDER BY name"
                )
            )
            tables = [row[0] for row in result.fetchall()]

        if not db_exists:
            message = "Banco de dados e tabelas criados com sucesso."
            logger.info(message)
        else:
            message = "Estrutura do banco de dados verificada."
            logger.info(message)

        tables_message = f"Tabelas disponíveis: {', '.join(tables)}"
        logger.info(tables_message)

    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {e}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Função utilitária que fornece uma sessão de banco de dados assíncrona.
    Injeção de dependência no app no lifespan.
    """
    async with AsyncSessionLocal() as session:
        yield session
    # chamada do session.close() acontece ao final do bloco async with().
