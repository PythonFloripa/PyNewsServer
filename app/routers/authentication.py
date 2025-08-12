from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services import auth
from app.services.database.community import get_community_by_username # Atualizar após banco de dados
from app.schemas import Token, TokenPayload, Community
import jwt
from jwt.exceptions import InvalidTokenError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/token")

def setup():
    router = APIRouter(prefix='/authentication', tags=['authentication'])

    async def authenticate_community(username: str, password: str):
        # Valida se o usuário existe e se a senha está correta
        db_user = await get_community_by_username(username)
        if not db_user or not auth.verify_password(password, db_user.password):
            return None
        return db_user

    @router.post("/token", response_model=Token)
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        # Rota de login: valida credenciais e retorna token JWT
        community = await authenticate_community(form_data.username, form_data.password)
        if not community:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciais inválidas"
            )
        # Community ex: email='alice@example.com' id=1 username='alice' full_name="Alice in the Maravilha's world" password='$2b$12$cA3fzLrRCmLp1aKn6ULhF.sQfaPQ70EoJU3Q0Szf6e4/YaVsKAAHS'
        payload = TokenPayload(username=community.username)
        token, expires_in = auth.create_access_token(data=payload)
        return {
            "access_token": token,
            "token_type": "Bearer",
            "expires_in": expires_in
        }


    @router.get("/me", response_model=Community)
    async def get_current_community(token: str = Depends(oauth2_scheme)):
        # Rota protegida: retorna dados do usuário atual com base no token
        creds_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload_dict = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
            payload = TokenPayload(**payload_dict)
        except (InvalidTokenError, ValueError):
            raise creds_exc

        community = get_community_by_username(payload.sub)
        if not community:
            raise creds_exc
        return community

    return router # Retorna o router configurado com as rotas de autenticação
