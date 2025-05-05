from .serializers import ProductSerializer
from .datechecker import get_total, datefromisoformat, DateRangePaginator
import asyncio 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required as lr 
from django.core.cache import cache
import pandas as pd
from .models import Settings, WeeklySpending, Product
from authentication.models import User
from collections.abc import Callable
from django.http import HttpRequest
from datetime import datetime, date 

def record(date:date, request:HttpRequest) -> dict:
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
def record2(date: date, products:list[dict]) -> dict:
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
def groupByDate(products: list[dict]) -> list[dict]:
    df = pd.DataFrame(products)
    if df.empty:
        return []
    df['date_for_grouping'] = (pd.to_datetime(df['date'], format='ISO8601').dt.date).apply(lambda x: x.isoformat())
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

def getAllProductsFromCache(user: User) -> list[dict]:
    products = cache.get(f'all-products-{user.username}')
    if products is None:
        products = ProductSerializer(user.products.all(), many=True).data
        cache.set(f'all-products-{user.username}', products)
    return products
        

def encryptAllProducts():
    for product in Product.objects.all(): 
        product.save() # saving indirectly encrypts the products


class EventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event_name:str, callback: Callable):
        """Register an event listener for a specific event."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def off(self, event_name:str, callback:Callable):
        """Remove an event listener for a specific event."""
        if event_name in self._events:
            self._events[event_name] = [cb for cb in self._events[event_name] if cb != callback]

    def emit(self, event_name:str, *args, **kwargs):
        """Trigger an event and call all registered listeners."""
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)

    def once(self, event_name: str, callback: Callable):
        """Register a one-time event listener for a specific event."""
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.off(event_name, wrapper)
        self.on(event_name, wrapper)
        
def getSettings(user: User):
    settings, created = Settings.objects.get_or_create(user=user)
    return settings
        
# Event handlers
def deleteAllProductsFromCache(request: HttpRequest, **kwargs):
    cache.delete(f'all-products-{request.user.username}')
    
def deleteQuickStatsFromCache(request: HttpRequest, **kwargs):
    cache.delete(f'weekly-stats-{request.user.username}')
    cache.delete(f'monthly-stats-{request.user.username}')
    
def deleteExpenditureRecordsFromCache(request: HttpRequest, **kwargs):
    cache.delete(f'records-{request.user.username}')

def updateWeeklySpendingData(request: HttpRequest, **kwargs):
    user = request.user
    dates = kwargs.get('dates')
    settings = getSettings(user)
    if settings.populated_weekly_spending:
        for date in dates:
            WeeklySpending.update_weekly_spending(user, date)
            
        
emitter = EventEmitter() # global event emitter
emitter.on('products_updated', deleteQuickStatsFromCache)
emitter.on('products_updated', deleteExpenditureRecordsFromCache)
emitter.on('products_updated', deleteAllProductsFromCache)
emitter.on('products_updated', updateWeeklySpendingData)

class ExpensePaginator: 
    
    def __init__(self, request:HttpRequest, number_of_days=7, extra_filters: dict = {}, use_cache=True, cache_key: str| None = None):
        if use_cache and cache_key is None: 
            raise ValueError("Cache key must be specified") 
        self.numberOfDays = number_of_days
        self.user: User = request.user
        self.dateRangePaginator = DateRangePaginator(
            self.user.date_joined.date(),
            datetime.today().date(),
            self.numberOfDays,
            reverse=True)
        self.extra_filters = extra_filters
        self.use_cache = use_cache
        self.cache_key = cache_key
    
    def get_page(self, page_number: int):
        """
          cached data is a list of pages 
          A page is a dictionary containing the records to display: [{}, {}, ..., {}]
        """
        if self.use_cache:
            cachedData: list[dict] | None = cache.get(self.cache_key)
            if cachedData is None:
                data = self.get_data(1)
                cache.set(self.cache_key, [data])
                return data
            
            if cachedData is not None and page_number <= len(cachedData):
                return {
                    'from_cache': True,
                    'pages': cachedData,
                    'nextPageNumber':self.get_next_page_number(len(cachedData))
                }
            
            if cachedData is not None and page_number > len(cachedData):
                data = self.get_data(page_number)
                cache.set(self.cache_key, cachedData + [data])
                return data
        return self.get_data(page_number)
    
    def get_data(self, page_number:int):
        dateRange = self.dateRangePaginator.get_date_range(page_number)
        if self.dateRangePaginator.reverse:
            dateRange = sorted(dateRange) # make the smaller data come first 
        products = ProductSerializer(
            self.user.products.filter(date__date__range=(dateRange[0], dateRange[1]), **self.extra_filters),
            many=True).data
        records = groupByDate(products)
        return {
            'from_cache': False,
            'records': records, 
            'nextPageNumber':self.get_next_page_number(page_number)
        }
        

    def get_next_page_number(self, current_page_number: int) -> int | None:
        if current_page_number < self.dateRangePaginator.total_pages:
            return current_page_number + 1
        return None