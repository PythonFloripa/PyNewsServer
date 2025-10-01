from typing import Optional

from fastapi import Request
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community


async def get_community_by_username(
    username: str,
    session: AsyncSession,
) -> Optional[Community]:
    """
    Busca e retorna um membro da comunidade pelo nome de usuário.
    Retorna None se o usuário não for encontrado.
    """
    # Cria a declaração SQL para buscar a comunidade pelo nome de usuário
    statement = select(Community).where(Community.username == username)

    # Executa a declaração na sessão e retorna o primeiro resultado
    result = await session.exec(statement)
    community = result.first()

    return community


async def create_community(
    request: Request,
    community: Community,  # community model
) -> Optional[Community]:
    """
    Cria um novo membro da comunidade.
    Somente usuário autenticado e com role Admin podem executar.
    """
    session: AsyncSession = request.app.db_session_factory
    session.add(community)
    await session.commit()
    await session.refresh(community)

    return community
