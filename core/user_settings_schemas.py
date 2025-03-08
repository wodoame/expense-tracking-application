from pydantic import BaseModel

class SearchSchema(BaseModel):
    indexed: bool = False
    product_schema_id: int = -1