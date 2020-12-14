from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database
from . import utils


def insert_security(params):
    db, db_cursor = get_cursor()
    query = f"""
        INSERT INTO watchlist (user_name, security_symbol, exchange_name)
        VALUES ('{params['user_name']}', '{params['security_symbol']}', '{params['exchange_name']}')
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)
    return 