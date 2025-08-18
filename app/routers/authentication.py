from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel.ext.asyncio.session import AsyncSession
import jwt
from jwt.exceptions import InvalidTokenError

from app.services import auth
from app.schemas import Token, TokenPayload, Community
from app.services.database.models import Community as DBCommunity
from app.services.database.community import get_community_by_username

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/token")

def setup(get_db_session_dep):
    router = APIRouter(prefix='/authentication', tags=['authentication'])
    async def authenticate_community(username: str, password: str, session: AsyncSession = Depends(get_db_session_dep)):
        # Valida se o usuário existe e se a senha está correta
        found_community = await get_community_by_username(
        username=username,
        session=session
    )
        if not found_community or not auth.verify_password(password, found_community.password):
            return None
        return found_community


    #### Teste 

    @router.post("/create_commumity")
    async def create_community( session: AsyncSession = Depends(get_db_session_dep)):
        password = "123Asd!@#"
        hashed_password=auth.hash_password(password)
        community = DBCommunity(username="username", email="username@test.com", password=hashed_password)
        session.add(community)
        await session.commit()
        await session.refresh(community)
        return {'msg':'succes? '}
    #### Teste 

    @router.post("/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: AsyncSession = Depends(get_db_session_dep)) :
        # Rota de login: valida credenciais e retorna token JWT
        community = await authenticate_community(form_data.username, form_data.password, session)
        if not community:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        payload = TokenPayload(username=community.username)
        token, expires_in = auth.create_access_token(data=payload)
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }
    return router # Retorna o router configurado com as rotas de autenticação
