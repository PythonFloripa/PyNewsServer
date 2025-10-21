#!/usr/bin/env python3
"""
Example script demonstrating how to create a community programmatically.

This script shows how to use the create_community function to add
a new community with a hashed password to the database.
"""

import asyncio
import os
import sys

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.auth import hash_password  # noqa: E402
from app.services.database.database import (  # noqa: E402
    AsyncSessionLocal,
    init_db,
)
from app.services.database.models.communities import Community  # noqa: E402


async def create_community_example():
    """Example of creating a community with hashed password."""

    # Initialize database
    await init_db()
    print("Database initialized successfully")

    # Community data
    username = "example_user"
    email = "example@domain.com"
    plain_password = "my_secure_password_123"

    print(f"Creating community for: {username}")
    print(f"Email: {email}")
    print("Password will be hashed before storing")

    # Hash the password using the hash_password function
    hashed_password = hash_password(plain_password)
    print(f"Password hashed: {hashed_password[:20]}... (truncated)")

    # Create new community instance
    new_community = Community(
        username=username,
        email=email,
        password=hashed_password.decode("utf-8"),  # Convert bytes to string
    )

    # Save to database using async session
    async with AsyncSessionLocal() as session:
        session.add(new_community)
        await session.commit()
        await session.refresh(new_community)

        print("\n✅ Community created successfully!")
        print(f"   ID: {new_community.id}")
        print(f"   Username: {new_community.username}")
        print(f"   Email: {new_community.email}")
        print(f"   Created at: {new_community.created_at}")
        print(f"   Updated at: {new_community.updated_at}")

        # Verify the password hash is stored correctly
        print(f"   Stored password hash: {new_community.password[:30]}...")


if __name__ == "__main__":
    asyncio.run(create_community_example())
