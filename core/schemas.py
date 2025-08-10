from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    id: int
    name: str
    description: str
    price: float
    date: str  # ISO8601 format

class Record(BaseModel):
    date: str  # ISO8601 format
    products: List[Product]
    total: float