from .models import Product
from .serializers import ProductSerializer
from .datechecker import get_total, datefromisoformat
import asyncio 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required as lr 
from django.core.cache import cache
import pandas as pd
from .models import Settings

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

# reduces access to the database by filtering through an already serialized result
def record2(date, products:list[dict]):
    filteredProducts = []
    for product in products:
        if datefromisoformat(product.get('date')).date() == date:
            filteredProducts.append(product)
    result = {
        'date': date, 
        'products': filteredProducts, 
        'total':get_total(filteredProducts)
    }
    
    return result

# This version uses pandas
def groupByDate(products):
    df = pd.DataFrame(products)
    df['date_for_grouping'] = (pd.to_datetime(df['date']).dt.date).apply(lambda x: x.isoformat())
    grouped = df.groupby('date_for_grouping')
    records = [{'date': date , 'products': group.to_dict('records'), 'total': float(group['price'].sum())} for date, group in grouped]
    return records
    

def login_required(cls):
    cls = method_decorator(lr(login_url='signin'), name='dispatch')(cls)
    return cls

def getRecordSkeletonContext(row_count=5, card_count=5):
    return {
        'row_count': range(row_count),
        'card_count': range(card_count)
    }

def getCategoriesSkeletonContext():
    return {
        'card_count': range(5)
    }

def encryptAllProducts():
    for product in Product.objects.all(): 
        product.save() # saving indirectly encrypts the products


class EventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event_name, callback):
        """Register an event listener for a specific event."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def off(self, event_name, callback):
        """Remove an event listener for a specific event."""
        if event_name in self._events:
            self._events[event_name] = [cb for cb in self._events[event_name] if cb != callback]

    def emit(self, event_name, *args, **kwargs):
        """Trigger an event and call all registered listeners."""
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)

    def once(self, event_name, callback):
        """Register a one-time event listener for a specific event."""
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.off(event_name, wrapper)
        self.on(event_name, wrapper)
        
def getSettings(user):
    settings, created = Settings.objects.get_or_create(user=user)
    return settings
        

def deleteQuickStatsFromCache(request):
    cache.delete(f'weekly-stats-{request.user.username}')
    cache.delete(f'monthly-stats-{request.user.username}')
    
def deleteExpenditureRecordsFromCache(request):
    cache.delete(f'records-{request.user.username}')
    
emitter = EventEmitter() # global event emitter
emitter.on('products_updated', deleteQuickStatsFromCache)
emitter.on('products_updated', deleteExpenditureRecordsFromCache)
