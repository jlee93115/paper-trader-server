import re

from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor
from . import utils

    

def get_securities(filters):
    db_cursor = get_cursor()
    query = f"""
        SELECT security_symbol, exchange_name 
        FROM {filters['table_name']}
        WHERE {filters['table_name']}.user_id = (SELECT user_id FROM users WHERE users.user_name = '{filters['user_name']}')
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results


def get_price(symbol, exchange):
    db_cursor = get_cursor()
    query = f"""
        SELECT security_value
        FROM public_securities
        WHERE public_securities.security_symbol = '{symbol}' AND public_securities.exchange_name = '{exchange}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    result_float = float(result[0])
    return result_float


def get_quantity(user_name, symbol, exchange):
    db_cursor = get_cursor()
    query = f"""
        SELECT quantity
        FROM owned_securities
        WHERE 
            owned_securities.security_symbol = '{symbol}' AND 
            owned_securities.exchange_name = '{exchange}' AND
            owned_securities.user_id = (SELECT user_id FROM users WHERE users.user_name = '{user_name}')
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result[0]


def search(search_term):
    search_term_upper = search_term.upper()

    db_cursor = get_cursor()
    query = f"""
        SELECT security_symbol, security_name, security_value, exchange_name
        FROM public_securities
        WHERE 
            UPPER(public_securities.security_symbol) LIKE '%{search_term_upper}%' OR
            UPPER(public_securities.security_name) LIKE '%{search_term_upper}%'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchall()
    return result


def update(update_model:UpdateModel):
    collection = get_collection(update_model['collection_name'])
    update = { '$set': update_model['content']}
    request = collection.update_one(
        update_model['filter'], 
        update
    )

    result = {
        'modified_count': request.modified_count,
        'content': update_model['content']
    }
    return result


def insert(insert_model:InsertModel):
    collection = get_collection(insert_model['collection_name'])

    request = collection.update_one(
        insert_model.content
    )

    response = {
        'modified_count': request.modified_count,
        'content': insert_model.update
    }
    return JSONResponse(content=response)