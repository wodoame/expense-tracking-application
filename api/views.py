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
from core.user_settings_schemas import SearchSchema
from core.utils import getSettings
from core.templatetags.custom_filters import dateOnly, timesince
from core.datechecker import datefromisoformat
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
        data = self.search_products(query, user)
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
    
    @staticmethod
    def search_products(query:str, user) -> dict:
        schema_id_file = 'product_schema_id.txt'
        if not os.path.exists(schema_id_file):
            setSchemaId(schema_id_file, -1)
        
        product_schema_id, created = KeyValuePair.objects.get_or_create(key='product_schema_id', defaults={'value':'0'})
        # Recreate index if schema ids stored in the file and database don't match
        if int(getSchemaId(schema_id_file)) != int(product_schema_id.value):
            recreate_index('products_index', schema_id_file, getCurrentProductSchema(), product_schema_id.value)
            
        schema = getCurrentProductSchema()
        # Create or open the index
        index_dir = 'products_index'
        if not index.exists_in(index_dir):
            os.makedirs(index_dir, exist_ok=True)
            ix = index.create_in(index_dir, schema)
        else:
            ix = index.open_dir(index_dir)

        # Add documents to the index
        writer = ix.writer()
        if not isIndexed(ix, user.id):
            print('user not index, index products')
            products = ProductSerializer(user.products.all(), many=True).data
            for product in products:
                writer.add_document(
                    id=product.get('id'),
                    doc_id=str(product.get('id')),
                    user_id=str(product.get('user')),
                    name=product.get('name'),
                    description=product.get('description'),
                    date=product.get('date'),
                    category=product.get('category'), 
                    price=product.get('price')
                    ) 
            writer.commit()

        with ix.searcher() as searcher:
            qp = MultifieldParser(['name', 'description'], ix.schema, group=OrGroup)
            
            # Perform a fuzzy search if it's just one word in the query (No special reason)
            if len(query.split(' ')) == 1:
                qp.add_plugin(FuzzyTermPlugin())
                q = qp.parse(f'{query}~') # edit distance is 1
            else:
                q = qp.parse(f'{query}')
            q = q & QueryParser('user_id', ix.schema).parse(str(user.id))
            print(q)
            results = searcher.search(q)
            data = {
                'query': query, 
                'type': 'Products',
                'total': results.has_exact_length(),
                'results': [
                 {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'description': result.get('description'),
                    'date': dateOnly(result.get('date')),
                    'price': result.get('price'),
                    'category': result.get('category'),
                    'date_timesince': timesince(datefromisoformat(result.get('date')).date())
                 }
                for result in results]
            }
            return data
        
class RecreateIndexes(APIView):
    def get(self, request):
        product_schema_id, created = KeyValuePair.objects.get_or_create(key='product_schema_id', defaults={'value': '0'})
        if not created:
            product_schema_id.value = str(int(product_schema_id.value) + 1)
            product_schema_id.save()
        return Response({'message': 'success'})