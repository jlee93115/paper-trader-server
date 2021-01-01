import re

from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils

def get_one_security(username: str, table_name: str, security_symbol: str, exchange: str):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE {table_name}.username = '{username}' AND
            {table_name}.security_symbol = '{security_symbol}' AND
            {table_name}.exchange_name = '{exchange}'
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
        SELECT SUM(quantity) AS quantity
        FROM owned_securities
        WHERE
            owned_securities.security_symbol = '{symbol}' AND
            owned_securities.exchange_name = '{exchange}' AND
            owned_securities.username = '{username}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result[0]

