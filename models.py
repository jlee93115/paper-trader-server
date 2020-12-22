from typing import Optional, Dict

from pydantic import BaseModel

class User(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str

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

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class OrderModel(BaseModel):
    token: str
    symbol: str
    exchange: str
    quantity: int = 0
    price: float = 0
