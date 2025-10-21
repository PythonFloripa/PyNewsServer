#!/usr/bin/env python3
"""
Simple script to add a community with command line arguments.

Usage:
    python scripts/create_community.py <username> <email> <password>

Example:
    python scripts/create_community.py john_doe john@example.com mypassword123
"""

import asyncio
import os
import sys

# Add the app directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.auth import hash_password  # noqa: E402
from app.services.database.database import (  # noqa: E402
    AsyncSessionLocal,
    init_db,
)
from app.services.database.models.communities import Community  # noqa: E402


async def create_community(
    username: str, email: str, password: str
) -> Community:
    """
    Create a new community in the database with hashed password.

    Args:
        username (str): The community username
        email (str): The community email
        password (str): The plain text password (will be hashed)

    Returns:
        Community: The created community object
    """
    # Initialize database if needed
    await init_db()

    # Hash the password before storing it
    hashed_pwd = hash_password(password)

    # Create new community instance
    new_community = Community(
        username=username,
        email=email,
        password=hashed_pwd.decode("utf-8"),  # Convert bytes to string
    )

    # Save to database
    async with AsyncSessionLocal() as session:
        session.add(new_community)
        await session.commit()
        await session.refresh(new_community)

    return new_community


async def main():
    """Main function to create community from command line arguments."""
    if len(sys.argv) != 4:
        print(
            "Usage: python scripts/create_community.py "
            "<username> <email> <password>"
        )
        print(
            "Example: python scripts/create_community.py "
            "john_doe john@example.com mypass123"
        )
        sys.exit(1)

    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]

    try:
        print(f"Creating community for user: {username}")
        community = await create_community(username, email, password)

        print("✅ Community created successfully!")
        print(f"   ID: {community.id}")
        print(f"   Username: {community.username}")
        print(f"   Email: {community.email}")
        print(f"   Created at: {community.created_at}")

    except Exception as e:
        print(f"❌ Error creating community: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
