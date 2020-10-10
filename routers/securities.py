from paper_trader.crud.securities import get_price, get_quantity
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.config import API_KEY, BASE_URL
router = APIRouter()


@router.get('/securities/get-watchlist/{user_name}')
def get_watchlist(user_name):
    # TODO: authentication
    filters = {
        'user_name': user_name,
        'table_name': 'watchlist'
    }
    try: 
        watchlists = crud.securities.get_securities(filters)
        watchlists_combined = {}
        for tuple in watchlists:
            price = get_price(tuple[0], tuple[1])
            watchlists_combined.update({tuple[0]: price})
        return JSONResponse(content=watchlists_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


@router.get('/securities/get-owned-stocks/{user_name}')
def get_owned_stocks(user_name):
    # TODO: authentication
    filters = {
        'user_name': user_name,
        'table_name': 'owned_securities'
    }    
    try: 
        owned_stocks = crud.securities.get_securities(filters)
        owned_sec_combined = {}
        for tuple in owned_stocks:
            quantity = get_quantity(user_name, tuple[0], tuple[1])
            price = get_price(tuple[0], tuple[1])
            owned_sec_combined.update({tuple[0]: [price, quantity]})
        return JSONResponse(content=owned_sec_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


@router.get('/securities/search/{search_term}')
def search_stocks(search_term):
    try: 
        securities_list = []
        search_results = crud.securities.search(search_term)
        for tuple in search_results:
            securities_list.append((tuple[0], tuple[1], float(tuple[2]), tuple[3]))
        print(securities_list)
        return JSONResponse(content=securities_list)
    except:
        raise HTTPException(404, detail='Search failed')


@router.post('/securities/buy/{user_name}')
def buy_security(user_name, symbol: str = '', price: float = 0, buy_quantity: int = 0):
    if symbol:
        projection = {'_id': 0, 'user_name': 0}
        filter = {'user_name': user_name}
        data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
        try: 
            list_of_securities = crud.securities.get_doc(data)
            securities_dict = list_of_securities[0]['stocks']
            symbol_upper = symbol.upper()
            if symbol_upper in securities_dict.keys():
                # increase count of already owned security
                securities_dict[symbol_upper][0] = securities_dict[symbol_upper][0] + buy_quantity
            else:
                # insert new security to owned list
                securities_dict.update({symbol_upper: [buy_quantity, price]})
            content = {'stocks': securities_dict}
            data = {'collection_name': "owned_securities", "filter": filter, "content": content}
            result = crud.securities.update(data)
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@router.post('/securities/sell/{user_name}')
def sell_security(user_name, symbol: str = '', price: float = 0, sell_quantity: int = 0):
    if symbol:
        projection = {'_id': 0, 'user_name': 0}
        filter = {'user_name': user_name}
        data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
        try: 
            list_of_securities = crud.securities.get_doc(data)
            securities_dict = list_of_securities[0]['stocks']
            symbol_upper = symbol.upper()

            original_quantity = securities_dict[symbol_upper][0]
            
            if original_quantity < sell_quantity:
                return JSONResponse(content='You can\'t sell more than what you own!')

            # decrement count of already owned security
            if original_quantity > sell_quantity:
                securities_dict[symbol_upper][0] = securities_dict[symbol_upper][0] - sell_quantity
            elif original_quantity == sell_quantity:
                del securities_dict[symbol_upper]
            
            content = {'stocks': securities_dict}
            data = {'collection_name': "owned_securities", "filter": filter, "content": content}
            result = crud.securities.update(data)
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')