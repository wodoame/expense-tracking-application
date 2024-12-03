from .models import Product
from .serializers import ProductSerializer
from .datechecker import get_total
import asyncio 
def intentionalDelay(seconds): 
    asyncio.sleep(seconds)

def record(date):
    products = ProductSerializer(Product.objects.filter(date__date=date), many=True).data
    result = {
        'date': date, 
        'products': products, 
        'total':get_total(products)
    }
    
    # intentionalDelay(2)
    return result

