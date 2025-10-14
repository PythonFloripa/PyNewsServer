from app.services.encryption import decrypt_email, encrypt_email


async def test_encrypt_email(email: str = "test@mail.com"):
    """Test the encrypt email."""
    encrypted_email = encrypt_email(email)

    assert email == decrypt_email(encrypted_email)
