from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import get_current_user
from paper_trader.models import OrderModel

router = APIRouter()

# Axios only allows request body with POST/PUT requests
@router.post('/watchlist/watched')
def get_watchlist(token: Token):
    user = get_current_user(token.access_token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try: 
        results = crud.watchlist.get_watched_securities(user['username'])
        watchlist = {}
        for stock in results:
            price = crud.utils.get_price(stock['security_symbol'], stock['exchange_name'])
            watchlist.update({stock['security_symbol']: [price, stock['exchange_name']]})
        return JSONResponse(content=watchlist)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


@router.post('/watchlist/watch')
def watch(order: OrderModel):
    user = get_current_user(order.token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        watchlist = crud.utils.get_one_security(user['username'], 'watchlist', order.symbol, order.exchange)
        if (len(watchlist) == 0):
            crud.watchlist.insert_security(user['username'], order.symbol, order.exchange)
            data = {
                'username': user['username'],
                'security_symbol': order.symbol,
                'exchange_name': order.exchange,
            }
            result = {'inserted_data': data}
            return JSONResponse(content=result)
    except:
        raise HTTPException(404, detail='Failed to add security to watchlist')


@router.post('/watchlist/unwatch')
def unwatch(order: OrderModel):
    user = get_current_user(order.token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if order.symbol:
        data = {
            'username': user['username'],
            'security_symbol': order.symbol,
            'exchange_name': order.exchange,
            'table_name': 'watchlist'
        }
        try: 
            crud.utils.delete_security(data)
            
            result = {'deleted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')