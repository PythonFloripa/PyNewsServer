import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services.database.models import Community
from app.services.database.orm.community import (
    create_community,
    get_community_by_username,
)
from app.services.encryption import decrypt_email, encrypt_email

# Dados de teste
TEST_USERNAME = "test_user_crypto"
TEST_EMAIL = "crypto@test.com"
TEST_PASSWORD = "@SafePassword123"


@pytest.mark.asyncio
async def test_insert_communities(session: AsyncSession):
    community = Community(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
    )
    session.add(community)
    await session.commit()
    await session.refresh(community)

    statement = select(Community).where(Community.username == TEST_USERNAME)
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.username == TEST_USERNAME
    assert found.email == TEST_EMAIL
    assert found.password == TEST_PASSWORD


@pytest.mark.asyncio
async def test_community_orm_flow_with_encryption_transparency(
    session: AsyncSession,
):
    """
    Testa a criação e a leitura de uma comunidade, validando
    que o ORM (propriedades) garante a transparência da criptografia.
    """
    new_community = Community(
        username=TEST_USERNAME,
        email=TEST_EMAIL,
        password=TEST_PASSWORD,
    )

    # 2. Ação: Use a função ORM para criar a comunidade
    created_community = await create_community(
        community=new_community, session=session
    )

    # 3. Asserção de Leitura Transparente (getters)
    # Ao acessar 'created_community.email', ele DEVE retornar o email descriptografado
    assert decrypt_email(created_community.email) == TEST_EMAIL
    assert created_community.username == TEST_USERNAME


#    stored_email = created_community.email

#   assert stored_email == TEST_EMAIL


@pytest.mark.asyncio
async def test_get_community_by_username_orm(session: AsyncSession):
    """
    Testa a função de leitura 'get_community_by_username' e a descriptografia.
    """
    # 1. Preparação: Crie um registro diretamente no banco para garantir
    # que o teste não dependa da função create_community
    community_to_insert = Community(
        username="newreader_test",
        email=encrypt_email(TEST_EMAIL),
        password=TEST_PASSWORD,
    )

    session.add(community_to_insert)
    await session.commit()
    await session.refresh(community_to_insert)

    # 2. Ação: Use a função ORM para buscar o registro
    found_community = await get_community_by_username(
        username="newreader_test", session=session
    )

    # 3. Asserções
    assert found_community is not None

    # O email lido deve ser o valor original (descriptografado pelo modelo)
    assert found_community.email == TEST_EMAIL
    assert found_community.username == "newreader_test"

    # Garante que a senha está correta (embora não seja o foco, é bom manter)
    assert found_community.password == TEST_PASSWORD
