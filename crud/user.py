from paper_trader.db.database import get_cursor, commit_to_database

def get_user(username):
    db, db_cursor = get_cursor()
    query = f"""
        SELECT *
        FROM users
        WHERE users.username = '{username}'
        """
    db_cursor.execute(query)
    result = db_cursor.fetchone()
    return result