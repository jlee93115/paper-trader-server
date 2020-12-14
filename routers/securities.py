from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from paper_trader import crud
from paper_trader.core.config import API_KEY, BASE_URL
router = APIRouter()


@router.get('/securities/get/{user_name}')
def get_owned_stocks(user_name):
    # TODO: authentication
    filters = {
        'user_name': user_name,
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


@router.post('/securities/buy/{user_name}')
def buy_security(user_name, symbol: str = '', price: float = 0, buy_quantity: int = 0, exchange_name: str =''):
    if symbol:
        data = {
            'user_name': user_name, 
            'security_symbol': symbol, 
            'exchange_name': exchange_name,
            'quantity': buy_quantity,
            'price': price
        }
        try: 
            crud.securities.insert_transaction(data)
            result = {'inserted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to purchase security')


@router.post('/securities/sell/{user_name}')
def sell_security(user_name, symbol: str = '', price: float = 0, sell_quantity: int = 0, exchange_name: str = ''):
    if symbol:
        data = {
            'user_name': user_name, 
            'security_symbol': symbol, 
            'exchange_name': exchange_name,
            'quantity': -(sell_quantity),
            'price': price,
            'table_name': 'owned_securities'
        }
        try: 
            original_quantity = crud.utils.get_quantity(user_name, symbol, exchange_name)
            if original_quantity < sell_quantity:
                raise HTTPException(422, detail='Cannot sell more than you own')

            crud.securities.insert_transaction(data)
            if original_quantity == sell_quantity:
                crud.utils.delete_security(data)
            
            result = {'deleted_data': data}
            return JSONResponse(content=result)
        except:
            raise HTTPException(404, detail='Failed to sell security')