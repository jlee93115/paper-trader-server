import requests
import json
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

API_KEY = 'Tsk_98e3de4393c349e29c06bc3479e7f7ff'
BASE_URL = 'https://sandbox.iexapis.com/'
params = {'token': API_KEY}


@app.get('/get-watchlist/{user_name}')
def get_watchlist(user_name):
    # TODO: authentication

    projection = {'_id': 0, 'user_name': 0, 'list_name': 0}
    filter = {'user_name': user_name}
    data = {'collection_name': "watchlists", "filter": filter, "projection": projection}
    try: 
        response = requests.get(url='http://localhost:8001/get-docs', json=data)
        watchlists_combined = {}
        for list in response.json():
            watchlists_combined.update(list['stocks'])
        return JSONResponse(content=watchlists_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')

    # for symbol in watchlist:
    #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params=params)
    #     watchlist[symbol] = float(r.text)

    # watchlist = Watchlists[0]['stocks']



@app.get('/get-owned-stocks/{user_name}')
def get_watchlist(user_name):
    # TODO: authentication
    projection = {'_id': 0, 'user_name': 0}
    filter = {'user_name': user_name}
    data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
    try: 
        response = requests.get(url='http://localhost:8001/get-docs', json=data)
        owned_sec_combined = {}
        for list in response.json():
            owned_sec_combined.update(list['stocks'])
        return JSONResponse(content=owned_sec_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')

    # for symbol in watchlist:
    #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params=params)
    #     watchlist[symbol] = float(r.text)


@app.get('/search-stocks/{search_term}')
def search_stocks(search_term):
    projection = {'_id': 0}
    data = {'collection_name': "public_securities", 'search_term': search_term, 'projection': projection}
    try: 
        response = requests.get(url='http://localhost:8001/search', json=data)
        return JSONResponse(content=response.json())
    except:
        raise HTTPException(404, detail='Search failed')


@app.post('/buy/{user_name}')
def buy_security(user_name, symbol: str = '', price: float = 0, quantity: int = 0):
    if symbol:
        projection = {'_id': 0, 'user_name': 0}
        filter = {'user_name': user_name}
        data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
        try: 
            request = requests.get(url='http://localhost:8001/get-docs', json=data)
            securities_dict = request.json()[0]['stocks']
            symbol_upper = symbol.upper()
            if symbol_upper in securities_dict.keys():
                # increase count of already owned security
                securities_dict[symbol_upper][0] = securities_dict[symbol_upper][0] + quantity
            else:
                # insert new security to owned list
                securities_dict.update({symbol_upper: [quantity, price]})
            
            content = {'stocks': securities_dict}
            data = {'collection_name': "owned_securities", "filter": filter, "content": content}
            request = requests.post(url='http://localhost:8001/update', json=data)
            return JSONResponse(content=request.json())
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@app.post('/sell/{user_name}')
def sell_security(user_name, symbol: str = '', price: float = 0, sell_quantity: int = 0):
    if symbol:
        projection = {'_id': 0, 'user_name': 0}
        filter = {'user_name': user_name}
        data = {'collection_name': "owned_securities", "filter": filter, "projection": projection}
        try: 
            request = requests.get(url='http://localhost:8001/get-docs', json=data)
            securities_dict = request.json()[0]['stocks']
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
            request = requests.post(url='http://localhost:8001/update', json=data)
            return JSONResponse(content=request.json())
        except:
            raise HTTPException(404, detail='Failed to sell security')