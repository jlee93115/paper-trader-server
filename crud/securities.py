import re

from fastapi.responses import JSONResponse

from paper_trader.models import DocumentModel, SearchModel, UpdateModel, InsertModel
from paper_trader.db.database import get_collection
from . import utils


# def count_docs(document_model: DocumentModel):
#     collection = get_collection(document_model)
#     request = collection.count_documents(document_model.filter)
    

def get_doc(document_model: DocumentModel):
    doc_list = []
    collection = get_collection(document_model['collection_name'])
    
    request = collection.find(document_model['filter'], projection=document_model['projection'])
    for item in request:
        doc_list.append(item)
    return doc_list


def search_docs(search_model: SearchModel):
    doc_list = []
    query_lower = search_model['search_term'].lower()
    query_upper = search_model['search_term'].upper()
    regex = re.compile(r'^.*('+query_lower + r')|('+query_upper+r').*')
    filter = {'$or': [ {'symbol': {'$regex': regex}}, {'name': {'$regex': regex}} ] }
    collection = get_collection(search_model['collection_name'])
    results = collection.find(filter=filter, projection=search_model['projection'])
    for item in results:
        print(item)
        doc_list.append(item)
    return doc_list


def update(update_model:UpdateModel):
    collection = get_collection(update_model['collection_name'])
    update = { '$set': update_model['content']}
    request = collection.update_one(
        update_model['filter'], 
        update
    )

    result = {
        'modified_count': request.modified_count,
        'content': update_model['content']
    }
    return result


def insert(insert_model:InsertModel):
    collection = get_collection(insert_model['collection_name'])

    request = collection.update_one(
        insert_model.content
    )

    response = {
        'modified_count': request.modified_count,
        'content': insert_model.update
    }
    return JSONResponse(content=response)