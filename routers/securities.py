from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import get_current_user
from paper_trader.models import OrderModel

router = APIRouter()


# Axios only allows request body with POST/PUT requests
@router.post('/securities/owned')
def get_securities(token: Token):
    user = get_current_user(token.access_token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        owned_stocks = {}
        results = crud.securities.get_owned_securities(user['username'])
        for stock in results:
            stock_details = [
                float(stock['avg']),
                stock['sum'],
                stock['exchange_name']
            ]
            owned_stocks.update({
                stock['security_symbol']: stock_details
            })
        return JSONResponse(content=owned_stocks)
    except:
        raise HTTPException(404, detail='Failed to retrieve owned stocks')


@router.get('/securities/search')
def search_stocks(q):
    try:
        securities_list = []
        search_results = crud.securities.search(q)
        for tuple in search_results:
            securities_list.append((tuple[0], tuple[1], float(tuple[2]), tuple[3]))
        return JSONResponse(content=securities_list)
    except:
        raise HTTPException(404, detail='Search failed')


@router.post('/securities/buy')
def buy(order: OrderModel):
    user = get_current_user(order.token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    cost = order.quantity * order.price
    if user['current_funds'] < cost:
        raise HTTPException(422, detail='Insufficient funds')

    data = {
        'username': user['username'],
        'security_symbol': order.symbol,
        'exchange_name': order.exchange,
        'quantity': order.quantity,
        'price': order.price
    }
    try:
        crud.securities.insert_transaction(data)
        result = {'purchased_security': data}
        return JSONResponse(content=result)
    except:
        raise HTTPException(404, detail='Failed to purchase security')


@router.post('/securities/sell')
def sell(order: OrderModel):
    user = get_current_user(order.token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    data = {
        'username': user['username'],
        'security_symbol': order.symbol,
        'exchange_name': order.exchange,
        'quantity': -(order.quantity),
        'price': order.price,
        'table_name': 'owned_securities'
    }
    try:
        original_quantity = crud.utils.get_quantity(user['username'], order['symbol'], order['exchange'])
        if original_quantity < order['quantity']:
            raise HTTPException(422, detail='You cannot sell more than you own')

        crud.securities.insert_transaction(data)
        if original_quantity == order['quantity']:
            crud.utils.delete_security(data)

        result = {'sold_security': data}
        return JSONResponse(content=result)
    except:
        raise HTTPException(404, detail='Failed to sell security')