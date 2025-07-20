from rest_framework.views import APIView
from core.serializers import * 
from rest_framework.response import Response 
from rest_framework.request import Request
from core.models import *
from django.db.models import Q
from .utils import * 
from core.templatetags.custom_filters import dateOnly, timesince
from core.datechecker import datefromisoformat
from django.core.cache import cache
from rest_framework import status
from .models import ErrorLog
from django.core.paginator import Paginator

class Status(APIView):
    def get(self, request):
        return Response({'status': 'ok', 'message': 'API is reachable.'})

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
        sqlQuery =  Q(name__icontains=query) | Q(description__icontains=query)
        limit = 10
        paginator = Paginator(user.products.filter(sqlQuery).order_by('-date'), limit)
        products = ProductSerializer(paginator.page(page_number).object_list, many=True).data
        data = {
            'query': query, 
            'type': 'Products',
            'total': len(products),
            'results': [
                {
                'id': product.get('id'),
                'name': product.get('name'),
                'description': product.get('description'),
                'date': dateOnly(product.get('date')),
                'raw_date': datetime.fromisoformat(product.get('date')).strftime('%Y-%m-%d'),
                'price': product.get('price'),
                'category': product.get('category'),
                'date_timesince': timesince(datefromisoformat(product.get('date')).date())
                }
            for product in products]
        }
        return data

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


class GetWeeklySpendings(APIView):
    def get(self, request):
        user = request.user
        limit = request.query_params.get('limit')
        page = int(request.query_params.get('page', 1))
        query = user.weekly_spendings.all().order_by('-week_start')
        if limit: 
            query = query[:int(limit)]
        paginator = Paginator(query, 10)
        number_of_pages = paginator.num_pages
        try:
            weekly_spendings = WeeklySpendingSerializer(paginator.page(page).object_list, many=True).data
            return Response({
                'weekly_spendings': weekly_spendings,
                'current_page': page,
                'number_of_pages': number_of_pages
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    