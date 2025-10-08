import pytest
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.routers.admin.routes import create_admin
from app.services.auth import verify_password
from app.services.database.models import Community
from app.services.encryption import decrypt_email

# Dados de teste
TEST_USERNAME = "test_user_crypto"
TEST_EMAIL = "crypto@test.com"
TEST_PASSWORD = "@SafePassword123"
import os


@pytest.mark.asyncio
async def test_insert_admin(session: AsyncSession):
    ADMIN_USER = os.getenv("ADMIN_USER")
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

    community = Community(
        username=ADMIN_USER,
    )

    await create_admin(session)
    statement = select(Community).where(community.username == ADMIN_USER)
    result = await session.exec(statement)
    found = result.first()

    assert found is not None
    assert found.username == ADMIN_USER
    assert decrypt_email(found.email) == ADMIN_EMAIL
    assert verify_password(ADMIN_PASSWORD, found.password)
