from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.config import API_KEY, BASE_URL
router = APIRouter()


@router.get('/securities/get-watchlist/{user_name}')
def get_watchlist(user_name):
    # TODO: authentication
    projection = {'_id': 0, 'user_name': 0, 'list_name': 0}
    filter = {'user_name': user_name}
    data = {'collection_name': "watchlists", "filter": filter, "projection": projection}
    try: 
        watchlists = crud.securities.get_doc(data)
        watchlists_combined = {}
        for list in watchlists:
            watchlists_combined.update(list['stocks'])
        return JSONResponse(content=watchlists_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')

#     # for symbol in watchlist:
#     #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params={'token': API_KEY})
#     #     watchlist[symbol] = float(r.text)

#     # watchlist = Watchlists[0]['stocks']


@router.get('/securities/get-owned-stocks/{user_name}')
def get_owned_stocks(user_name):
    # TODO: authentication
    projection = {'_id': 0, 'user_name': 0}
    filter = {'user_name': user_name}
    data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
    try: 
        owned_stocks = crud.securities.get_doc(data)
        owned_sec_combined = {}
        for list in owned_stocks:
            owned_sec_combined.update(list['stocks'])
        return JSONResponse(content=owned_sec_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')

    # for symbol in watchlist:
    #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params={'token': API_KEY})
    #     watchlist[symbol] = float(r.text)


@router.get('/securities/search/{search_term}')
def search_stocks(search_term):
    projection = {'_id': 0}
    data = {'collection_name': "public_securities", 'search_term': search_term, 'projection': projection}
    try: 
        found_securities = crud.securities.search_docs(data)
        return JSONResponse(content=found_securities)
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