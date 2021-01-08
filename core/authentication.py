from datetime import datetime, timedelta, timezone, tzinfo
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import HTTPException, Depends, status, Cookie

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

    # access token is valid for 2 minutes
    expire = datetime.utcnow() + timedelta(minutes=2)
    to_encode.update({"exp": expire})
    to_encode.update({'iat': datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt


def create_refresh_token(data: dict):
    # Initialize datetime object
    expiry = datetime.now()

    to_encode = data.copy()
    valid_token = crud.authentication.get_valid_refresh_token(data['sub'])
    if valid_token is None:
        # refresh token is valid for 30 days
        expiry = datetime.now() + timedelta(days=30)
    else:
        expiry = valid_token['expiry'].replace(tzinfo=None)

    to_encode.update({"exp": expiry})
    to_encode.update({'iat': datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    # implement refresh token rotation
    crud.authentication.revoke_refresh_tokens(data['sub'])
    crud.authentication.insert_refresh_token(data['sub'], encoded_jwt, expiry)
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


def validate_refresh_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
        username: str = payload.get("sub")
        if username is None:
            return None
        token_data = TokenData(username=username)
        token_status = crud.authentication.get_refresh_token_status(token_data.username, token)
        if token_status is None:
            return None

        # Convert local time to timezone of expiry time and compare
        expiry_timezone = token_status['expiry'].utcoffset()
        tz = timezone(expiry_timezone)
        current_date_aware = datetime.now(tz)

        if(token_status['expired'] == False):
            if (token_status['expiry'] > current_date_aware):
                user = crud.users.get_user(token_data.username)
                return user
        crud.authentication.revoke_refresh_tokens(token_data.username)
    except:
        return None
