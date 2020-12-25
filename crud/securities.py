from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils


def get_owned_securities(username: str, table_name: str = 'owned_securities', order_by: str = 'security_symbol', order: str = 'ASC' ):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT AVG(price), SUM(quantity), security_symbol, exchange_name
        FROM {table_name}
        WHERE {table_name}.username = '{username}'
        GROUP BY security_symbol, exchange_name
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
        INSERT INTO transactions (username, security_symbol, exchange_name, price, quantity)
        VALUES ('{params['username']}', '{params['security_symbol']}', '{params['exchange_name']}', {params['price']}, {params['quantity']})
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return 
