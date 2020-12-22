from paper_trader.models import Token
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.authentication import is_authenticated
from paper_trader.models import OrderModel

router = APIRouter()


# Axios only allows request body with POST/PUT requests
@router.post('/securities/owned')
def get_owned_stocks(token: Token):
    user = is_authenticated(token.access_token)
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    filters = {
        'username': user['username'],
        'table_name': 'owned_securities'
    }    
    try: 
        owned_stocks = crud.utils.get_securities(filters)
        owned_sec_combined = {}
        for tuple in owned_stocks:
            if tuple[2] in owned_sec_combined:
                total_quantity = owned_sec_combined[tuple[2]][1] + tuple[5]
                total_value = owned_sec_combined[tuple[2]][0] * owned_sec_combined[tuple[2]][1] + float(tuple[4]) * tuple[5]
                avg_value = total_value / total_quantity
            else:
                total_quantity = tuple[5]
                avg_value = float(tuple[4])
            owned_sec_combined.update({tuple[2]: [avg_value, total_quantity, tuple[3]]})
        return JSONResponse(content=owned_sec_combined)
    except:
        raise HTTPException(404, detail='Failed to retrieve watchlists')


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
            'quantity': order.quantity,
            'price': order.price
        }
        try: 
            crud.securities.insert_transaction(data)
            result = {'inserted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@router.post('/securities/sell')
def sell(order: OrderModel):
    user = is_authenticated(order['token'])
    if user is None:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if order['symbol']:
        data = {
            'username': user['username'],
            'security_symbol': order['symbol'],
            'exchange_name': order['exchange'],
            'quantity': -(order['quantity']),
            'price': order['price'],
            'table_name': 'owned_securities'
        }
        try: 
            original_quantity = crud.utils.get_quantity(user['username'], order['symbol'], order['exchange'])
            if original_quantity < order['quantity']:
                raise HTTPException(422, detail='You cannot sell more than you own')

            crud.securities.insert_transaction(data)
            if original_quantity == order['quantity']:
                crud.utils.delete_security(data)
            
            result = {'deleted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')