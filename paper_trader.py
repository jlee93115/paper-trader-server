import requests
from typing import Optional
import json

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from data import Users, OwnedStocks, Watchlists, Stock_db

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_KEY = ''
BASE_URL = 'https://sandbox.iexapis.com/'
params = {'token': API_KEY}


@app.get('/get-watchlist/{user_id}')
def get_watchlist(user_id):

    # TODO: authentication

    # watchlist = Users[0]['watchlist']
    # for symbol in watchlist:
    #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params=params)
    #     watchlist[symbol] = float(r.text)

    watchlist = Watchlists[0]['stocks']
    print(watchlist)
    return JSONResponse(content=watchlist)


@app.get('/get-owned-stocks/{user_id}')
def get_watchlist(user_id):

    # TODO: authentication

    # watchlist = Users[0]['watchlist']
    # for symbol in watchlist:
    #     r = requests.get('https://sandbox.iexapis.com/stable/stock/' + symbol + '/price', params=params)
    #     watchlist[symbol] = float(r.text)

    owned_stocks = OwnedStocks[0]['stocks']
    return JSONResponse(content=owned_stocks)

@app.get('/search-stocks/{symbolQuery}')
def search_stocks(symbolQuery):
    with open('./data/stock_db.json', 'r') as file:
        data = json.load(file)

    search_result = []
    for dict in data:
        if (symbolQuery.upper() in dict['symbol']):
            search_result.append(dict)
    return JSONResponse(content=search_result)
