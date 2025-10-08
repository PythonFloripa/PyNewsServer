import os

from cryptography.fernet import Fernet

test_encryption_key = "r0-QKv5qACJNFRqy2cNZCsfZ_zVvehlC-v8zDJb--EI="
# print(Fernet.generate_key())
# Carrega a chave da variável de ambiente
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", test_encryption_key)

if not ENCRYPTION_KEY:
    raise RuntimeError(
        "ENCRYPTION_KEY não está definida nas variáveis de ambiente."
    )

cipher = Fernet(ENCRYPTION_KEY)


def encrypt_email(email: str) -> str:
    """Criptografa uma string de e-mail."""
    encrypted_email = cipher.encrypt(email.encode())
    return encrypted_email


def decrypt_email(encrypted_email: str) -> str:
    """Descriptografa uma string de e-mail."""
    print("decipher email called")
    return cipher.decrypt(encrypted_email).decode()
