from whoosh.fields import Schema, TEXT, ID, STORED

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