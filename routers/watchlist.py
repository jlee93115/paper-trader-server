from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import is_authenticated
from paper_trader.models import OrderModel

router = APIRouter()

# Axios only allows request body with POST/PUT requests
@router.post('/watchlist/watched')
def get_watchlist(token: Token):
    user = is_authenticated(token.access_token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    filters = {
        'username': user['username'],
        'table_name': 'watchlist'
    }
    try: 
        watchlists = crud.utils.get_securities(filters)
        watchlists_combined = {}
        for tuple in watchlists:
            price = crud.utils.get_price(tuple[2], tuple[3])
            watchlists_combined.update({tuple[2]: [price, tuple[3]]})
        return JSONResponse(content=watchlists_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


@router.post('/watchlist/watch')
def watch(order: OrderModel):
    user = is_authenticated(order.token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if order.symbol:
        try:
            filters = {
                'username': user['username'],
                'table_name': 'watchlist',
                'security_symbol': order.symbol,
                'exchange_name': order.exchange
            }
            watchlist = crud.utils.get_one_security(filters)

            if (len(watchlist) == 0):
                params = {
                    'username': user['username'],
                    'security_symbol': order.symbol,
                    'exchange_name': order.exchange,
                }
                crud.watchlist.insert_security(params)
                result = {'inserted_data': params}
                return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@router.post('/watchlist/unwatch')
def unwatch(order: OrderModel):
    user = is_authenticated(order.token)
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