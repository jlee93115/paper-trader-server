from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database


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
