from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community
from app.services.encryption import decrypt_email, encrypt_email


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
    community_result = result.first()

    # add tratamento de descriptografia do email
    if community_result is not None:
        # evitar mutação direta e cache
        community = community_result.model_copy()
        community.email = decrypt_email(community.email)
    else:
        community = None
    return community  # add community not found treatment?


async def create_community(
    session: AsyncSession,
    community: Community,  # community model
) -> Optional[Community]:
    """
    Cria um novo membro da comunidade.
    Somente usuário autenticado e com role Admin podem executar.
    """
    community.email = encrypt_email(community.email)
    session.add(community)
    await session.commit()
    await session.refresh(community)

    return community
