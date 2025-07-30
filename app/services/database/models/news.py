from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field

class News(SQLModel, table=True):
    __tablename__ = "news"

    # Campos obrigatórios e suas definições
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str # = Field(index=True) # Indexado para buscas mais rápidas por título
    content: str
    author: str # Informação esta no endpoint e não aparece no schema do db
    category: str
    user_email: str
    source_url: str
    tags: str # Poderia ser uma lista de strings em um modelo mais complexo, mas por simplicidade mantemos como string
    social_media_url: str
    likes: int = Field(default=0) # Valor padrão de 0 curtidas

    # Chaves estrangeiras
    community_id: Optional[int] = Field(default=None, foreign_key="communities.id")
    # library_id: Optional[int] = Field(default=None, foreign_key="libraries.id")

    # Campos de data/hora
    created_at: Optional[datetime] = Field(default_factory=datetime.now) # Preenchido automaticamente na criação
    updated_at: Optional[datetime] = Field(default_factory=datetime.now, sa_column_kwargs={"onupdate": datetime.now}) # Atualizado automaticamente na modificação
