from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database

def get_watched_securities(username: str, table_name: str = 'watchlist', order_by: str = 'security_symbol', order: str = 'ASC' ):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT security_symbol, exchange_name
        FROM {table_name}
        WHERE {table_name}.username = '{username}'
        ORDER BY {order_by} {order}
        """
    db_cursor.execute(query)
    results = db_cursor.fetchall()
    return results


def insert_security(username: str, security_symbol: str, exchange_name: str):
    db, db_cursor = get_cursor()
    query = f"""
        INSERT INTO watchlist (username, security_symbol, exchange_name)
        VALUES ('{username}', '{security_symbol}', '{exchange_name}')
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return 


def delete_security(table_name: str, username: str, symbol: str, exchange: str):
    db, db_cursor = get_cursor()
    query = f"""
        DELETE FROM {table_name}
        WHERE
            {table_name}.username = '{username}' AND
            {table_name}.security_symbol = '{symbol}' AND
            {table_name}.exchange_name = '{exchange}'
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return