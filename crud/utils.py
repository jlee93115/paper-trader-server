from pymongo.collection import Collection
from paper_trader.models import DocumentModel, SearchModel


def get_doc(document_model: DocumentModel):
    doc_list = []
    collection = get_collection(document_model)
    
    request = collection.find(document_model['filter'], projection=document_model['projection'])
    for item in request:
        doc_list.append(item)
    return doc_list

    
