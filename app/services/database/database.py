# database.py
import os
from typing import AsyncGenerator

from sqlmodel import SQLModel, create_engine, Field
from sqlalchemy.orm import sessionmaker

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import AsyncEngine

# --- Configuração do Banco de Dados ---
# Usamos 'sqlite+aiosqlite' para suporte assíncrono com SQLite
SQLITE_PATH = os.getenv('SQLITE_PATH', 'pynews.db') # Valor padrão se não definida
SQLITE_URL = os.getenv('SQLITE_URL', f'sqlite+aiosqlite:///{SQLITE_PATH}')

DATABASE_FILE = SQLITE_PATH # Usamos SQLITE_PATH para o nome do arquivo
DATABASE_URL = SQLITE_URL # Usamos SQLITE_URL para a URL completa

# Cria o motor assíncrono 
engine: AsyncEngine = AsyncEngine(create_engine(DATABASE_URL, echo=True, future=True))

# --- Fábrica de Sessões Assíncronas ---
# Crie a fábrica de sessões UMA VEZ no escopo global do módulo.
# Esta é a variável é injetada para obter sessões nas chamadas. 
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False # expire_on_commit=False é importante!
)

# --- Modelo de Teste Temporário (SQLModel) ---
class TestEntry(SQLModel, table=True): # table=True indica que esta classe é um modelo de tabela
    """
    Classe de modelo temporária para testes de conexão com o banco de dados.
    Será usada como uma solução provisória antes da implementação dos modelos finais do projeto.
    """
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
    # Verifica se o arquivo do banco de dados existe
    if not os.path.exists(DATABASE_FILE):
        print(f"Arquivo de banco de dados '{DATABASE_FILE}' não encontrado. Criando novo banco de dados e tabelas.")
        async with engine.begin() as conn:
            # SQLModel.metadata.create_all é síncrono e precisa ser executado via run_sync
            await conn.run_sync(SQLModel.metadata.create_all)
        print("Tabelas criadas com sucesso.")
    else:
        print(f"Arquivo de banco de dados '{DATABASE_FILE}' já existe. Conectando.")

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Função utilitária que fornece uma sessão de banco de dados assíncrona.
    Injeção de dependência no app no lifespan. 
    """
    # Agora, usa a fábrica de sessões global AsyncSessionLocal
    async with AsyncSessionLocal() as session:
        yield session
    # chamada do session.close() acontece ao final do bloco with. 

"""  
Testes enquanto a implementação dos modelos finais do projeto não estão nos arquivos.
"""
''' 
# --- Funções CRUD de Exemplo (Opcional) ---
async def create_test_entry(session: AsyncSession, message: str) -> TestEntry:
    """Cria uma nova entrada de teste no banco de dados."""
    new_entry = TestEntry(message=message)
    session.add(new_entry)
    await session.commit()
    await session.refresh(new_entry)
    return new_entry

async def get_test_entries(session: AsyncSession) -> list[TestEntry]:
    """Retorna todas as entradas de teste do banco de dados."""
    from sqlmodel import select # Importa select para consultas desse testes 
    result = await session.exec(select(TestEntry))
    return result.scalars().all()
 '''