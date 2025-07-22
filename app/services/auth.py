from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.schemas import TokenPayload
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY", "default_fallback_key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 20))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain, hashed): 
    # Verifica se a senha passada bate com a hash da comunidade
    return pwd_context.verify(plain, hashed)

def get_password_hash(password): 
    # Retorna a senha em hash para salvar no banco de dados
    return pwd_context.hash(password)

def create_access_token(data: TokenPayload, expires_delta: timedelta | None = None):
    """
    Gera um token JWT contendo os dados do usuário (payload) e uma data de expiração.

    Parâmetros:
    - data (TokenPayload): Dicionário com os dados que serão codificados no token. Deve conter a chave 'sub' com o identificador do usuário.
    - expires_delta (timedelta | None): Tempo até o token expirar. Se não fornecido, usará o padrão de 20 minutos.

    Retorna:
    - str: Token JWT assinado.
    - int: tempo de expiração em segundos
    """
    if not expires_delta:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": data.username, "exp": expire}
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return token, int(expires_delta.total_seconds())
