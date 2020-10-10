from typing import Optional, Dict

from pydantic import BaseModel

class DocumentModel(BaseModel):
    collection_name: str
    filter: Dict = {}
    projection: Dict = {}

class SearchModel(BaseModel):
    collection_name: str
    search_term: str
    projection: Dict = {}

class UpdateModel(BaseModel):
    collection_name: str
    filter: Dict = {}
    content: Dict

class InsertModel(BaseModel):
    collection_name: str
    filter: Dict = {}
    content: Dict