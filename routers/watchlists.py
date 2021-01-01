from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import get_current_user
from paper_trader.models import OrderModel

router = APIRouter()

@router.get('/watchlists/watched-securities')
def get_watchlist(current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try: 
        results = crud.watchlists.get_watched_securities(current_user['username'])
        watchlist = []
        for stock in results:
            price = crud.utils.get_price(stock['security_symbol'], stock['exchange_name'])
            watchlist.append({
                'symbol': stock['security_symbol'],
                'price': price,
                'exchange': stock['exchange_name']
            })
        return JSONResponse(content=watchlist)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


@router.post('/watchlists/watched-securities')
def add_security_to_watchlist(order: OrderModel, current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        watchlist = crud.utils.get_one_security(current_user['username'], 'watchlist', order.symbol, order.exchange)
        if (len(watchlist) == 0):
            crud.watchlists.insert_security(current_user['username'], order.symbol, order.exchange)
            data = {
                'username': current_user['username'],
                'security_symbol': order.symbol,
                'exchange_name': order.exchange,
            }
            result = {'inserted_data': data}
            return JSONResponse(content=result)
    except:
        raise HTTPException(404, detail='Failed to add security to watchlist')


@router.delete('/watchlists/watched-securities')
def remove_security_from_watchlist(order: OrderModel, current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if order.symbol:
        try: 
            crud.watchlists.delete_security(
                'watchlist',
                current_user['username'],
                order.symbol, 
                order.exchange
            )
            
            data = {
                'username': current_user['username'],
                'security_symbol': order.symbol,
                'exchange_name': order.exchange,
                'table_name': 'watchlist'
            }
            result = {'removed_security': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')