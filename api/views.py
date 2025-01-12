from rest_framework.views import APIView
from core.serializers import CategorySerializer, CategorySerializerWithMetrics
from rest_framework.response import Response 

class Categories(APIView):
    def get(self, request):
        user = request.user 
        categories = None
        if request.query_params.get('metrics'): 
            categories = CategorySerializerWithMetrics(user.categories.all(), many=True).data
        else: 
            categories = CategorySerializer(user.categories.all(), many=True).data
        return Response(categories)

