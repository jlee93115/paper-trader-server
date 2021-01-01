from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import get_current_user
from paper_trader.models import OrderModel

router = APIRouter()

@router.get('/trades/owned-securities')
def get_owned_securities(current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        results = crud.trades.get_owned_securities(current_user['username'])
        owned_securities = []
        for security in results:
            price = crud.utils.get_price(security['security_symbol'], security['exchange_name'])
            owned_securities.append({
                'symbol': security['security_symbol'],
                'price': float(price),
                'quantity': security['sum'],
                'exchange': security['exchange_name']
            })
        return JSONResponse(content=owned_securities)
    except:
        raise HTTPException(422, detail='Failed to retrieve owned stocks')


@router.post('/trades/owned-securities')
def buy(order: OrderModel, current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    cost = order.quantity * order.price
    if current_user['current_funds'] < cost:
        raise HTTPException(422, detail='Insufficient funds')

    data = {
        'username': current_user['username'],
        'symbol': order.symbol,
        'exchange': order.exchange,
        'quantity': order.quantity,
        'price': order.price,
        'transaction_type': 'buy'
    }
    try:
        crud.trades.insert_transaction(data)
        response = {'order': data}
        return JSONResponse(content=response)
    except:
        raise HTTPException(422, detail='Failed to purchase security')


@router.delete('/trades/owned-securities')
def sell(order: OrderModel, current_user = Depends(get_current_user)):
    if current_user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        owned_quantity = crud.utils.get_quantity(current_user['username'], order.symbol, order.exchange)
        if owned_quantity < order.quantity:
            raise HTTPException(422, detail='Order quantity exceeds owned quantity')

        security_transactions = crud.trades.get_transactions(current_user['username'], order.symbol, order.exchange, 'owned_securities')
        order_quantity = order.quantity
        while order_quantity > 0:
            if order_quantity == security_transactions[0]['quantity']:
                crud.trades.delete_transaction(
                    'owned_securities', 
                    security_transactions[0]['transaction_id'], 
                    current_user['username'], 
                    order.symbol, 
                    order.exchange
                )
                order_quantity -= security_transactions[0]['quantity']
            elif order_quantity > security_transactions[0]['quantity']:
                crud.trades.delete_transaction(
                    'owned_securities', 
                    security_transactions[0]['transaction_id'], 
                    current_user['username'], 
                    order.symbol, 
                    order.exchange
                )
                order_quantity -= security_transactions[0]['quantity']
                security_transactions.pop(0)
            elif order_quantity < security_transactions[0]['quantity']:
                crud.trades.update_quantity(
                    'owned_securities', 
                    security_transactions[0]['transaction_id'], 
                    current_user['username'], 
                    order.symbol, 
                    order.exchange, 
                    security_transactions[0]['quantity'] - order_quantity
                )
                order_quantity = 0
        data = {
            'username': current_user['username'],
            'symbol': order.symbol,
            'exchange': order.exchange,
            'quantity': -(order.quantity),
            'price': order.price,
            'transaction_type': 'sell',
        }
        crud.trades.insert_transaction(data)
        response = {'order': data}
        return JSONResponse(content=response)
    except:
        raise HTTPException(422, detail='Failed to sell security')
