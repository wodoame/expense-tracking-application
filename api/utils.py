import os 
from whoosh import index
from whoosh.qparser import QueryParser
from whoosh.fields import Schema, TEXT, ID, STORED
from core.utils import EventEmitter
from authentication.models import User
from django.core.cache import cache
        
def recreate_index(index_dir: str, schema_id_file: str, new_schema: Schema, new_schema_id: int):
    """Recreate the index with the new schema."""
    os.makedirs(index_dir, exist_ok=True)
    ix = index.create_in(index_dir, new_schema)
    setSchemaId(schema_id_file, new_schema_id)
    print(f"Created new index with updated schema")

def getSchemaId(path:str):
    with open(path, 'r') as f: 
        schemaId = int(f.read().strip())
    return schemaId

def setSchemaId(path:str, schemaId:int):
    with open(path, 'w') as f: 
        f.write(str(schemaId)) 

def updateIndex(product:dict, method='update'):
    """Update the index: add, edit or delete an item from the index"""
    index_dir = 'products_index'
    if not index.exists_in(index_dir):
        print('no index exists')
        return
    
    ix = index.open_dir(index_dir)
    if isIndexed(ix, product.get('user')):
        writer = ix.writer()
        if method == 'update':
            writer.update_document(
                id=product.get('id'),
                doc_id=str(product.get('id')),
                user_id=str(product.get('user')),
                name=product.get('name'),
                description=product.get('description'),
                date=product.get('date'),
                category=product.get('category'), 
                price=product.get('price')
                )
    
        if method == 'delete':
            writer.delete_by_term('doc_id', str(product.get('id')))
        writer.commit() 
    
def isIndexed(ix:index.Index, user_id:int):
    # Step 1: search for an item with the user's id
    # Step 2: If at least one exists then items have been indexed
    q = QueryParser('user_id', ix.schema).parse(str(user_id))
    with ix.searcher() as searcher:
        results = searcher.search(q, limit=1)
        return not results.is_empty()
    
def page_is_cached(user: User, page_number):
    res = cache.get(f'{user.username}-search-page')
    return (res is not None) and page_number <= res
        
def getCurrentProductSchema(): 
    # Define the schema
    # NOTE: if you change the schema visit /api/recreate-indexes/ 
    # This helps to clear the current index and use the new schema for creating a new index
    schema = Schema(
        id=STORED, doc_id=ID(unique=True),
        user_id=ID,  name=TEXT(stored=True),
        description=TEXT(stored=True),
        date=STORED,
        category=STORED,
        price=STORED, 
        page_number=ID, # page number the search result exists on
        )
    return schema

indexEventEmitter = EventEmitter()
indexEventEmitter.on('product_updated', updateIndex)