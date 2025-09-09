from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.schemas import Community, Token, TokenPayload
from app.services import auth
from app.services.database.models import Community as DBCommunity
from app.services.database.orm.community import get_community_by_username
from app.services.limiter import limiter

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/token")


def setup():
    router = APIRouter(prefix="/authentication", tags=["authentication"])

    async def authenticate_community(
        request: Request, username: str, password: str
    ):
        # Valida se o usuário existe e se a senha está correta
        session: AsyncSession = request.app.db_session_factory
        found_community = await get_community_by_username(
            username=username, session=session
        )
        if not found_community or not auth.verify_password(
            password, found_community.password
        ):
            return None
        return found_community

    # Teste
    async def get_current_community(
        request: Request,
        token: Annotated[str, Depends(oauth2_scheme)],
    ) -> DBCommunity:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(
                token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM]
            )
            username = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenPayload(username=username)
        except InvalidTokenError:
            raise credentials_exception
        session: AsyncSession = request.app.db_session_factory
        community = await get_community_by_username(
            session=session, username=token_data.username
        )
        if community is None:
            raise credentials_exception

        return community

    async def get_current_active_community(
        current_user: Annotated[DBCommunity, Depends(get_current_community)],
    ) -> DBCommunity:
        # A função simplesmente retorna o usuário.
        # Pode ser estendido futuramente para verificar um status "ativo".
        return current_user

    # Teste

    @router.post("/create_commumity")
    async def create_community(request: Request):
        password = "123Asd!@#"
        hashed_password = auth.hash_password(password)
        community = DBCommunity(
            username="username",
            email="username@test.com",
            password=hashed_password,
        )
        session: AsyncSession = request.app.db_session_factory
        session.add(community)
        await session.commit()
        await session.refresh(community)
        return {"msg": "succes? "}

    # Teste

    @router.post("/token", response_model=Token)
    @limiter.limit("60/minute")
    async def login_for_access_token(
        request: Request, form_data: OAuth2PasswordRequestForm = Depends()
    ):
        # Rota de login: valida credenciais e retorna token JWT
        community = await authenticate_community(
            request, form_data.username, form_data.password
        )
        if not community:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas",
            )
        payload = TokenPayload(username=community.username)
        token, expires_in = auth.create_access_token(data=payload)
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in,
        }

    @router.get("/me", response_model=Community)
    @limiter.limit("60/minute")
    async def read_community_me(
        request: Request,
        current_community: Annotated[
            DBCommunity, Depends(get_current_active_community)
        ],
    ):
        # Rota para obter informações do usuário autenticado
        return current_community

    return router  # Retorna o router configurado com as rotas de autenticação
