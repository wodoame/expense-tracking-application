from rest_framework.views import APIView
from core.serializers import * 
from rest_framework.response import Response 
from rest_framework.request import Request
from core.models import *
from django.db.models import Q
from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import MultifieldParser, OrGroup, FuzzyTermPlugin, QueryParser
import os
from .utils import * 

class Categories(APIView):
    def get(self, request):
        user = request.user 
        categories = None
        if request.query_params.get('metrics'): 
            categories = CategorySerializerWithMetrics(user.categories.all(), many=True).data
        else: 
            categories = CategorySerializer(user.categories.all(), many=True).data
        return Response(categories)


class Search(APIView):
    def get(self, request: Request):
        query = request.query_params.get('query').strip()
        user = request.user
        products = ProductSerializer(user.products.all(), many=True).data
        data = self.search_products(query, products, user.id)
        return Response(data)
    
    def search_categories(self, query: str) -> dict:
        sqlQuery =  Q(name__icontains=query) | Q(description__icontains=query)
        categories = Category.objects.filter(sqlQuery)
        data = {
            'query': query,
            'type': 'Category',
            'total': categories.count(), 
            'results': CategorySerializer(categories, many=True).data
        }
        return data
    
    def search_products(self, query:str, products, user_id) -> dict:
        # Define the schema
        schema = Schema(id=STORED, doc_id=ID(unique=True), user_id=ID,  name=TEXT(stored=True), description=TEXT(stored=True))

        # Create or open the index
        index_dir = 'indexdir'
        if not index.exists_in(index_dir, indexname='products'):
            os.makedirs(index_dir, exist_ok=True)
            ix = index.create_in(index_dir, schema, indexname='products')
        else:
            ix = index.open_dir(index_dir, indexname='products')

        # Add documents to the index
        writer = ix.writer()
        for product in products:
            writer.update_document(id=product.get('id'), doc_id=str(product.get('id')), user_id=str(product.get('user')), name=product.get('name'), description=product.get('description'))
        writer.commit()
        with ix.searcher() as searcher:
            qp = MultifieldParser(['name', 'description'], ix.schema, group=OrGroup)
            
            # Perform a fuzzy search if it's just one word in the query (No special reason)
            if len(query.split(' ')) == 1:
                qp.add_plugin(FuzzyTermPlugin())
                q = qp.parse(f'{query}~') # edit distance is 1
            else:
                q = qp.parse(f'{query}')
            q = q & QueryParser('user_id', ix.schema).parse(str(user_id))
            print(q)
            results = searcher.search(q)
            data = {
                'query': query, 
                'type': 'Products',
                'total': len(results),
                'results': [dict(result) for result in results]
            }
            return data
        
class RecreateIndexes(APIView):
    def get(self, request):
        lines = read_flag()
        newlines = []
        indexname, value = lines[0].split(':')
        if int(value) == 1:
            pass
        
        newlines.append(f'{indexname}:0') # set value to zero
        
            
        return Response({'message': 'index recreated'})