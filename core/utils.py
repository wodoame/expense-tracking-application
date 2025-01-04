from .models import Product
from .serializers import ProductSerializer
from .datechecker import get_total
import asyncio 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required as lr 

def record(date, request):
    user = request.user
    products = ProductSerializer(user.products.filter(date__date=date), many=True).data
    result = {
        'date': date, 
        'products': products, 
        'total':get_total(products)
    }
    
    # asyncio.run(asyncio.sleep(2))
    return result

def login_required(cls):
    cls = method_decorator(lr(login_url='signin'), name='dispatch')(cls)
    return cls

def getRecordSkeletonContext():
    return {
        'row_count': range(5),
        'card_count': range(5)
    }

