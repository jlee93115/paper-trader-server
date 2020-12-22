from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from paper_trader import crud
from paper_trader.core.authentication import authenticate_user, create_access_token, is_authenticated


router = APIRouter()

@router.post('/users/login')
async def login(login_form: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(login_form.username, login_form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user['username']}
    )
    return {"access_token": access_token, "token_type": "bearer"}