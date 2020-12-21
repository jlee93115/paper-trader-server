from datetime import datetime, timedelta
from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from paper_trader import crud
from .utils import authenticate_user, create_access_token, get_current_user


router = APIRouter()

@router.post('/user/login')
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(login_form.username, login_form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user['username']}
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get('/user/me')
async def is_authenticated(token: Token):
    user = get_current_user(token.access_token)
    return user