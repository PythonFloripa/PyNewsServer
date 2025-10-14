#!/usr/bin/env python3
"""
Script to add a new community to the Community table with hashed password.

Usage:
    python scripts/add_community.py

The script will prompt for community details and hash the password.
"""

import asyncio
import os
import sys

# Add the app directory to the Python path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.auth import hash_password
from app.services.database.database import AsyncSessionLocal, init_db
from app.services.database.models.communities import Community


async def add_community(username: str, email: str, password: str) -> Community:
    """
    Add a new community to the database with hashed password.

    Args:
        username (str): The community username
        email (str): The community email
        password (str): The plain text password (will be hashed)

    Returns:
        Community: The created community object
    """
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


def get_user_input(prompt: str) -> str:
    """Get user input synchronously."""
    return input(prompt).strip()


async def main():
    """Main function to run the script interactively."""
    try:
        # Initialize database if needed
        await init_db()

        print("=== Add New Community ===")
        print("Please provide the following information:")

        # Get user input
        username = get_user_input("Username: ")
        if not username:
            print("Error: Username cannot be empty")
            return

        email = get_user_input("Email: ")
        if not email:
            print("Error: Email cannot be empty")
            return

        password = get_user_input("Password: ")
        if not password:
            print("Error: Password cannot be empty")
            return

        # Confirm before creating
        print("\nCreating community with:")
        print(f"  Username: {username}")
        print(f"  Email: {email}")
        print("  Password: [HIDDEN]")

        confirm = get_user_input("\nProceed? (y/N): ").lower()
        if confirm not in {"y", "yes"}:
            print("Operation cancelled.")
            return

        # Create the community
        print("\nCreating community...")
        community = await add_community(username, email, password)

        print("✅ Community created successfully!")
        print(f"   ID: {community.id}")
        print(f"   Username: {community.username}")
        print(f"   Email: {community.email}")
        print(f"   Created at: {community.created_at}")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
    except Exception as e:
        print(f"❌ Error creating community: {e}")
        raise


def create_community_programmatically(
    username: str, email: str, password: str
) -> Community:
    """
    Wrapper function to create a community programmatically.
    For use in other scripts.

    Args:
        username (str): The community username
        email (str): The community email
        password (str): The plain text password

    Returns:
        Community: The created community object
    """
    return asyncio.run(add_community(username, email, password))


if __name__ == "__main__":
    # Run the interactive script
    asyncio.run(main())
