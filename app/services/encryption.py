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
    var_test = cipher.encrypt(email.encode())
    print(f"cipher email {var_test}")
    var_test_de = cipher.decrypt(var_test).decode()
    print(f"decipher email {var_test_de}")
    return var_test


def decrypt_email(encrypted_email: str) -> str:
    """Descriptografa uma string de e-mail."""
    return cipher.decrypt(encrypted_email).decode()
