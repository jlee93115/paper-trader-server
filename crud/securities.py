import re

from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils


def get_purchase_value(symbol, exchange):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT security_value
        FROM public_securities
        WHERE public_securities.security_symbol = '{symbol}' AND public_securities.exchange_name = '{exchange}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    result_float = float(result[0])
    return result_float


def search(search_term):
    search_term_upper = search_term.upper()

    db, db_cursor = get_cursor()
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



def insert_transaction(params):
    db, db_cursor = get_cursor()
    query = f"""
        INSERT INTO transactions (user_name, security_symbol, exchange_name, price, quantity)
        VALUES ('{params['user_name']}', '{params['security_symbol']}', '{params['exchange_name']}', {params['price']}, {params['quantity']})
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return 
