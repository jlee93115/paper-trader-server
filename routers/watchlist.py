from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.config import API_KEY, BASE_URL

router = APIRouter()


@router.get('/watchlist/get/{user_name}')
def get_watchlist(user_name):
    # TODO: authentication
    filters = {
        'user_name': user_name,
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


@router.post('/watchlist/add/{user_name}')
def add_to_watchlist(user_name, symbol: str = '', exchange_name: str =''):
    if symbol:
        try:
            filters = {
                'user_name': user_name,
                'table_name': 'watchlist',
                'security_symbol': symbol,
                'exchange_name': exchange_name
            }
            watchlist = crud.utils.get_one_security(filters)

            if (len(watchlist) == 0):
                params = {
                    'user_name': user_name, 
                    'security_symbol': symbol, 
                    'exchange_name': exchange_name,
                }
                crud.watchlist.insert_security(params)
                result = {'inserted_data': params}
                return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@router.post('/watchlist/delete/{user_name}')
def delete_security(user_name, symbol: str = '', exchange_name: str = ''):
    if symbol:
        data = {
            'user_name': user_name, 
            'security_symbol': symbol, 
            'exchange_name': exchange_name,
            'table_name': 'watchlist'
        }
        try: 
            crud.utils.delete_security(data)
            
            result = {'deleted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')