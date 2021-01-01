from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm

from paper_trader import crud
from paper_trader.core.authentication import authenticate_user, create_access_token, get_current_user


router = APIRouter()

@router.post('/users/token')
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

    response = {
        'access_token': access_token,
        'token_type': 'bearer',
        'username': user['username'],
        'first_name': user['first_name'],
        'last_name': user['last_name'],
        'funds': user['current_funds']
    }
    return response

@router.get('/users/authenticated')
async def isAuthenticated(current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": current_user['username']}
    )
    response = {
        'access_token': access_token,
        'token_type': 'bearer',
        'username': current_user['username'],
        'first_name': current_user['first_name'],
        'last_name': current_user['last_name'],
        'funds': current_user['current_funds']
    }
    return response