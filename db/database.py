import json
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from paper_trader.models import InsertModel, UpdateModel, DocumentModel
from paper_trader.core.config import DB_NAME, DB_PORT, DB_URL


app = FastAPI()


def get_database():
    try:
        client = MongoClient(DB_URL, DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        raise HTTPException(status_code=404, detail='Failed to connect to database')


def get_collection(collection_name):
    try:
        database = get_database()
        collection = database[collection_name]
        return collection
    except:
        raise HTTPException(status_code=404, detail='Failed to get collection')