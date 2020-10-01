import json
from models import InsertModel, UpdateModel
import re

from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from models import DocumentModel, SearchModel

app = FastAPI()

DB_URL = 'localhost'
DB_PORT = 27017
DB_NAME = 'paper_trader'

def get_database():
    try:
        client = MongoClient(DB_URL, DB_PORT)
        db = client[DB_NAME]
        return db
    except:
        raise HTTPException(status_code=404, detail='Failed to connect to database')


@app.get('/find-docs')
def count_docs(document_model: DocumentModel):
    database = get_database()
    collection = database[document_model.collection_name]
    request = collection.count_documents(document_model.filter)
    

@app.get('/get-docs')
def getDocument(document_model: DocumentModel):
    doc_list = []
    database = get_database()
    collection = database[document_model.collection_name]

    request = collection.find(document_model.filter, projection=document_model.projection)
    for item in request:
        doc_list.append(item)
    return JSONResponse(content=doc_list)


@app.get('/search')
def searchDocs(search_model: SearchModel):
    doc_list = []
    query_lower = search_model.search_term.lower()
    query_upper = search_model.search_term.upper()
    regex = re.compile(r'^.*('+query_lower + r')|('+query_upper+r').*')
    filter = {'$or': [ {'symbol': {'$regex': regex}}, {'name': {'$regex': regex}} ] }

    database = get_database()
    collection = database[search_model.collection_name]

    results = collection.find(filter=filter, projection=search_model.projection)
    for item in results:
        doc_list.append(item)
    return JSONResponse(content=doc_list)


@app.post('/update')
def update(update_model:UpdateModel):
    database = get_database()
    collection = database[update_model.collection_name]

    update = { '$set': update_model.content}
    request = collection.update_one(
        update_model.filter, 
        update
    )

    response = {
        'modified_count': request.modified_count,
        'content': update_model.content
    }
    return JSONResponse(content=response)


@app.post('/insert')
def update(insert_model:InsertModel):
    database = get_database()
    collection = database[insert_model.collection_name]

    request = collection.update_one(
        insert_model.content
    )

    response = {
        'modified_count': request.modified_count,
        'content': insert_model.update
    }
    return JSONResponse(content=response)