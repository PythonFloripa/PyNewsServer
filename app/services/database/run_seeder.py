# run_seeder.py  -- para rodar manualmente 
import asyncio
from app.services.database.seeder import insert_test_community
from app.services.database.database import init_db

async def main():
    await init_db()
    await insert_test_community()

if __name__ == "__main__":
    asyncio.run(main())
