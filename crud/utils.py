import re

from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils
    

def get_securities(filters):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM {filters['table_name']}
        WHERE {filters['table_name']}.username = '{filters['username']}'
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results


def get_one_security(filters):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM {filters['table_name']}
        WHERE {filters['table_name']}.username = '{filters['username']}' AND
            {filters['table_name']}.security_symbol = '{filters['security_symbol']}' AND
            {filters['table_name']}.exchange_name = '{filters['exchange_name']}'            
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results


def get_price(symbol, exchange):
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


def get_quantity(username, symbol, exchange):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT quantity
        FROM owned_securities
        WHERE 
            owned_securities.security_symbol = '{symbol}' AND 
            owned_securities.exchange_name = '{exchange}' AND
            owned_securities.username = '{username}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result[0]


def delete_security(params):
    db, db_cursor = get_cursor()
    query = f"""
        DELETE FROM {params['table_name']}
        WHERE
            {params['table_name']}.username = '{params['username']}' AND
            {params['table_name']}.security_symbol = '{params['security_symbol']}' AND
            {params['table_name']}.exchange_name = '{params['exchange_name']}'
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return 