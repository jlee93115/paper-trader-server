from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils
from datetime import date, datetime
import time

def get_owned_securities(username: str, table_name: str = 'owned_securities', order_by: str = 'security_symbol', order: str = 'ASC' ):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT SUM(quantity), security_symbol, exchange_name
        FROM {table_name}
        WHERE {table_name}.username = '{username}'
        GROUP BY security_symbol, exchange_name
        ORDER BY {order_by} {order}
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results

def get_transactions(username: str, symbol: str, exchange:str, table_name: str, order_by: str = 'transaction_time', order: str = 'ASC' ):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM {table_name}
        WHERE
            {table_name}.username = '{username}' AND
            {table_name}.security_symbol = '{symbol}' AND
            {table_name}.exchange_name = '{exchange}'
        ORDER BY {order_by} {order}
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results

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


def insert_transaction(params):
    db, db_cursor = get_cursor()
    timestamp = datetime.utcnow()
    query = f"""
        INSERT INTO transactions (username, security_symbol, exchange_name, price, quantity, transaction_time, transaction_type)
        VALUES ('{params['username']}', '{params['symbol']}', '{params['exchange']}', {params['price']}, {params['quantity']}, '{timestamp}', '{params['transaction_type']}' )
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return


def delete_transaction(table_name: str, transaction_id, username: str, symbol: str, exchange: str):
    db, db_cursor = get_cursor()
    query = f"""
        DELETE FROM {table_name}
        WHERE
            {table_name}.username = '{username}' AND
            {table_name}.security_symbol = '{symbol}' AND
            {table_name}.exchange_name = '{exchange}' AND
            {table_name}.transaction_id = {transaction_id}
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return

    
def update_quantity(table_name: str, transaction_id, username: str, symbol: str, exchange: str, new_quantity: int):
    db, db_cursor = get_cursor()
    query = f"""
        UPDATE {table_name}
        SET quantity = {new_quantity}
        WHERE
            {table_name}.username = '{username}' AND
            {table_name}.security_symbol = '{symbol}' AND
            {table_name}.exchange_name = '{exchange}' AND
            {table_name}.transaction_id = {transaction_id}
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return