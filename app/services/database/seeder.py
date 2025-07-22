# app/services/database/seeder.py

async def insert_test_community():
    from app.services.database.database import AsyncSessionLocal  # import local para evitar circular import
    from app.services.database.model.community import Community
    from app.services.auth import get_password_hash
    from sqlmodel import select

    async with AsyncSessionLocal() as session:
        result = await session.exec(select(Community).where(Community.username == "alice"))
        if result.first():
            return

        user = Community(
            username="alice",
            full_name="Alice in the Maravilha's world",
            email="alice@example.com",
            password=get_password_hash("secret123")
        )
        session.add(user)
        await session.commit()
        print("Usuário de teste 'alice' criado com sucesso.")
