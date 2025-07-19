# app/services/database.py

from app.schemas import CommunityInDB

# Simulando um banco com hash de senha
from app.services.auth import get_password_hash

fake_users_db = {
    "alice": CommunityInDB(
        username="alice",
        full_name="Alice in the Maravilha's world",
        email="alice@example.com",
        password=get_password_hash("secret123")
    )
}

def get_community_by_username(username: str):
    return fake_users_db.get(username)
