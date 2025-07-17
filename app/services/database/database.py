# app/services/database.py

from app.schemas import UserInDB

# Simulando um banco com hash de senha
from app.services.auth import get_password_hash

fake_users_db = {
    "alice": UserInDB(
        username="alice",
        full_name="Alice Liddell",
        email="alice@example.com",
        password=get_password_hash("secret123")
    )
}

def get_community_by_username(username: str):
    return fake_users_db.get(username)
