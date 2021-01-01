from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status

from passlib.context import CryptContext
from secrets import token_hex
from jose import JWTError, jwt

from paper_trader import crud
from paper_trader.models import TokenData

SECRET_KEY = token_hex(32)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def get_password_hash(password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash(password)
    return hashed_password


def authenticate_user(username: str, password: str):
    user = crud.users.get_user(username)
    if not user:
        return False
    if not verify_password(password, user['password']):
        return False
    return user


def verify_password(entered_password, hash_password):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    return pwd_context.verify(entered_password, hash_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    
    # token is valid for 2 minutes
    expire = datetime.utcnow() + timedelta(minutes=2)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
    except JWTError:
        return None
    user = crud.users.get_user(token_data.username)
    return user