from rest_framework.views import APIView
from core.serializers import * 
from rest_framework.response import Response 
from rest_framework.request import Request
from core.models import *
from django.db.models import Q
from whoosh import index
from whoosh.qparser import MultifieldParser, OrGroup, FuzzyTermPlugin, QueryParser
import os
from .utils import * 
from core.templatetags.custom_filters import dateOnly, timesince
from core.datechecker import datefromisoformat
from django.core.cache import cache
from rest_framework import status
from .models import ErrorLog
from django.core.paginator import Paginator
from django.conf import settings

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
        data = self.search_products(query, user,  1)
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
    def search_products(query:str, user: User, page_number: int) -> dict:
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
        context = {}
        get_for_current_page_only = False # fetch search results which are found on other pages than the current page_number
        products = user.products.all()
        paginator = Paginator(products, settings.SEARCH_PAGE_SIZE) # NOTE: recreate the index if you change the page size
        latest_cached_page = cache.get(f'{user.username}-search-page')
        print(f'{latest_cached_page=}')
        if latest_cached_page is None or not isIndexed(ix, user.id): 
            latest_cached_page = None
            cache.set(f'{user.username}-search-page', latest_cached_page) # forcefully set it to None so that indexing can start all over again due to page_is_cached() returning False for page 1
            os.makedirs(index_dir, exist_ok=True)
            ix = index.create_in(index_dir, ix.schema)
        if page_is_cached(user, page_number):
            context['has_next_page'] = paginator.page(latest_cached_page).has_next() # check if the latest cached page has a next page
            if context['has_next_page']:
                context['next_page_number'] = latest_cached_page + 1
        elif not page_is_cached(user, page_number):
            cache.set(f'{user.username}-search-page', page_number)
            print(f'page {page_number} not index, index products')
            page = paginator.page(page_number)
            get_for_current_page_only = True
            context['has_next_page'] = page.has_next()
            context['next_page_number'] = page.next_page_number() if page.has_next() else None
            products = ProductSerializer(
                page.object_list,
                many=True,
                ).data 
            for product in products:
                writer.add_document(
                    id=product.get('id'),
                    doc_id=str(product.get('id')),
                    user_id=str(product.get('user')),
                    name=product.get('name'),
                    description=product.get('description'),
                    date=product.get('date'),
                    category=product.get('category'), 
                    price=product.get('price'), 
                    page_number=str(page_number)
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
            if not get_for_current_page_only:
                q = q & QueryParser('user_id', ix.schema).parse(str(user.id)) 
            else: # If all products have not been indexed then we need to get only the products for the current page
                q =  q & (QueryParser('page_number', ix.schema).parse(str(page_number)) & QueryParser('user_id', ix.schema).parse(str(user.id)))
            print(q)
            results = searcher.search(q)
            data = {
                'query': query, 
                'type': 'Products',
                'total': len(results),
                'context': context,
                'results': [
                 {
                    'id': result.get('id'),
                    'name': result.get('name'),
                    'description': result.get('description'),
                    'date': dateOnly(result.get('date')),
                    'raw_date': datetime.fromisoformat(result.get('date')).strftime('%Y-%m-%d'),
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
    
class ClearCache(APIView):
    def get(self, request):
        cache.clear()
        return Response({'message': 'cache cleared successfully'})
    
class ErrorLogs(APIView):
    def get(self, request):
        try: # Query all error logs, ordered by timestamp
            logs = ErrorLog.objects.all().values(
                'message', 'user__username', 'timestamp', 'stack_trace',
                'request_path', 'status_code', 'level', 'method', 'get_data', 'post_data', 'ip_address', 'error_type'
            )
            # Format logs for JSON response
            formatted_logs = [
                {
                    'error_type': log['error_type'],
                    'message': log['message'],
                    'username': log['user__username'] or 'Anonymous',
                    'timestamp': log['timestamp'],
                    'date': dateOnly(log['timestamp']),
                    'time_since': timesince(log['timestamp']),
                    'stack_trace': log['stack_trace'].splitlines() if log['stack_trace'] else [],
                    'request_path': log['request_path'],
                    'status_code': log['status_code'],
                    'level': log['level'],
                    'method': log['method'],
                    'get_data': log['get_data'],
                    'post_data': log['post_data'],
                    'ip_address': log['ip_address']
                }
                for log in logs
            ]
            return Response({'count': logs.count(), 'logs': formatted_logs}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)