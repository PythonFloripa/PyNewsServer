from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from app.services import auth, database
from app.schemas import Token, TokenData, User
import jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/token")

router = APIRouter(prefix="/authentication")

def authenticate_user(username: str, password: str):
    db_user = database.get_community_by_username(username)
    if not db_user or not auth.verify_password(password, db_user.password):
        return None
    return db_user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas")
    token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    from jwt.exceptions import InvalidTokenError
    creds_exc = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        username: str = payload.get("sub")
        if not username:
            raise creds_exc
    except InvalidTokenError:
        raise creds_exc
    user = database.get_community_by_username(username)
    if not user:
        raise creds_exc
    return user
