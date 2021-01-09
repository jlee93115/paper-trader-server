from psycopg2.extensions import JSON
from pyasn1.type.univ import Null
from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, Depends, status, Response, Cookie, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional

from paper_trader import crud
from paper_trader.core.authentication import authenticate_user, create_access_token, create_refresh_token, get_current_user, validate_refresh_token
from paper_trader.models import LogoutModel

router = APIRouter()

@router.post('/users/token')
async def login(response: Response, login_form: OAuth2PasswordRequestForm = Depends()):
    current_user = authenticate_user(login_form.username, login_form.password)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": current_user['username']}
    )
    refresh_token = create_refresh_token(
        data={"sub": current_user['username']}
    )
    content = {
        'access_token': access_token,
        'token_type': 'Bearer',
        'username': current_user['username'],
        'first_name': current_user['first_name'],
        'last_name': current_user['last_name'],
        'funds': float(current_user['current_funds'])
    }
    response = JSONResponse(content=content)

    # cookie expires in 30 days
    response.set_cookie('pt_refreshtoken', refresh_token, httponly=True, max_age=30*86400)
    return response


@router.post('/users/refresh-token')
async def refresh_tokens(pt_refreshtoken: Optional[str] = Cookie(None)):
    current_user = validate_refresh_token(pt_refreshtoken)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new tokens
    access_token = create_access_token(
        data={"sub": current_user['username']}
    )
    refresh_token = create_refresh_token(
        data={"sub": current_user['username']}
    )
    content = {
        'access_token': access_token,
        'token_type': 'Bearer',
        'username': current_user['username'],
        'first_name': current_user['first_name'],
        'last_name': current_user['last_name'],
        'funds': float(current_user['current_funds'])
    }
    response = JSONResponse(content=content)
    # Set cookie for refresh token with expiry of 30 days
    response.set_cookie('pt_refreshtoken', refresh_token, httponly=True, max_age=30*86400)
    return response


@router.get('/users/authenticated')
async def is_authenticated(current_user = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    content = {
        'username': current_user['username'],
        'first_name': current_user['first_name'],
        'last_name': current_user['last_name'],
        'funds': float(current_user['current_funds'])
    }
    return JSONResponse(content=content)


@router.patch('/users/logout')
async def logout(logout_model: LogoutModel):
    crud.authentication.revoke_refresh_tokens(logout_model.username)

    response = JSONResponse(content='Logged out successfully')
    response.delete_cookie('pt_refreshtoken')
    return response