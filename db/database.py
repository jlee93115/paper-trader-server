import psycopg2
from paper_trader.core.config import DB_NAME, DB_UN, DB_PW

def get_database():
    try:
        db = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_UN,
            password=DB_PW
        )
        return db
    except Exception as err:
        raise err


def get_cursor():
    try:
        db = get_database()
        cursor = db.cursor()
        return db, cursor
    except Exception as err:
        raise err


def commit_to_database(db, cursor):
    db.commit()
    cursor.close()
    db.close()