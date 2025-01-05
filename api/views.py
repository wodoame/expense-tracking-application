from rest_framework.views import APIView
from core.serializers import CategorySerializer
from rest_framework.response import Response 

class Categories(APIView):
    def get(self, request):
        user = request.user 
        categories = CategorySerializer(user.categories.all(), many=True).data
        return Response(categories)

