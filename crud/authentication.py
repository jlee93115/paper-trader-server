from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_cursor, commit_to_database


def insert_refresh_token(username: str, refresh_token: str, expiration_time):
    db, db_cursor = get_cursor()
    query = f"""
        INSERT INTO access_tokens (username, refresh_token, expiry, expired)
        VALUES ('{username}', '{refresh_token}', '{expiration_time}', false )
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)


def get_refresh_token_status(username: str, refresh_token: str):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT expiry, expired
        FROM access_tokens
        WHERE
            access_tokens.username = '{username}' AND
            access_tokens.refresh_token = '{refresh_token}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result


def get_valid_refresh_token(username: str):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM access_tokens
        WHERE
            access_tokens.username = '{username}' AND
            access_tokens.expired = 'false'

        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result


def revoke_refresh_tokens(username: str):
    db, db_cursor = get_cursor()
    query = f"""
        UPDATE access_tokens
        SET expired = 'true'
        WHERE
            access_tokens.username LIKE '{username}'
        """
    db_cursor.execute(query)
    commit_to_database(db, db_cursor)