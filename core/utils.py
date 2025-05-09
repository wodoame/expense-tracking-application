from .serializers import ProductSerializer
from .datechecker import get_total, datefromisoformat, DateRangePaginator
import asyncio 
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required as lr 
from django.core.cache import cache
import pandas as pd
from .models import Settings, WeeklySpending, Product
from django.db.models import Min
from authentication.models import User
from collections.abc import Callable
from django.http import HttpRequest
from datetime import datetime, date
from urllib.parse import quote 

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
    cache.delete(f'enhanced-pages-{request.user.username}')

def updateWeeklySpendingData(request: HttpRequest, **kwargs):
    user = request.user
    dates = kwargs.get('dates')
    if dates is not None:
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
          cachedData is a list of pages 
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
        """" get the page data based on the page number"""
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
    
class EnhancedExpensePaginator:
    def __init__(self, request:HttpRequest, cache_key: str, number_of_days=7, specific_category: bool = False, category_name='',  extra_filters: dict = {}):
        """ get the relevant dates (dates where things were actually purchased) """
        if specific_category and category_name == '': 
            raise ValueError('Category name must be specified')
        self.user = request.user
        self.extra_filters = extra_filters
        self.category_name = category_name
        self.specific_category = specific_category
        self.number_of_days = number_of_days
        self.cache_key = cache_key
        self.enhanced_pages = self.get_enhanced_pages()
    
    def get_enhanced_pages(self):
        """
        The DateRangePaginator produces pages that may be blank which slows down loading of content
        Enhanced pages are modified pages featuring times where purchases were actually made
        So no blank pages will be loaded
        """
        if self.specific_category: # if a category is specified, we need to filter by that category
            pages = cache.get(f'{quote(self.category_name)}-enhanced-pages-{self.user.username}') # check the cache if it already exists 
            if pages:
                return pages
            # get the relevant dates (dates where things were actually purchased)
            self.relevant_dates = self.user.products.filter(
                category__name=self.category_name,
                date__date__range=(self.user.date_joined.date(), datetime.today().date()) 
            ).values('date').annotate(min_date=Min('date__date')).values_list('min_date', flat=True)
            self.relevant_dates = list(sorted(self.relevant_dates, reverse=True))
        else: # if no category is specified, we need to filter by all products
            pages = cache.get(f'enhanced-pages-{self.user.username}') # check the cache if it already exist
            if pages:
                return pages
            self.relevant_dates = self.user.products.filter(
                date__date__range=(self.user.date_joined.date(), datetime.today().date())
            ).values('date').annotate(min_date=Min('date__date')).values_list('min_date', flat=True)
            self.relevant_dates = list(sorted(self.relevant_dates, reverse=True))
        enhanced_pages = {}    
        paginator = DateRangePaginator(
            self.user.date_joined.date(),
            datetime.today().date(),
            self.number_of_days,
            reverse=True)
        
        if self.relevant_dates:
            page = 1 
            new_page_number = 0
            i = 0 # to index the dates
            date = self.relevant_dates[i]
            while i < len(self.relevant_dates) and page <= paginator.get_total_pages(): # last condition may be redundant I'm not sure.
                current_date_range = sorted(paginator.get_date_range(page))
                if current_date_range[0] <= date <= current_date_range[1]:
                    new_page_number += 1
                while current_date_range[0] <= date <= current_date_range[1]:
                    if enhanced_pages.get(new_page_number) is None:
                        enhanced_pages[new_page_number] = current_date_range
                    i += 1
                    if i < len(self.relevant_dates):
                        date = self.relevant_dates[i]
                    else:
                        break
                    
                page += 1
        if self.specific_category:
            cache.set(f'{quote(self.category_name)}-enhanced-pages-{self.user.username}', enhanced_pages)
        else:
            cache.set(f'enhanced-pages-{self.user.username}', enhanced_pages)            
        return enhanced_pages
                
                
    def get_total_pages(self):
        return len(self.enhanced_pages)
                
            
        
    def get_page(self, page: int):
        # cached data for all is just a list of pages. [{}, {}, {}, ]
        cached_data: list[dict] = cache.get(self.cache_key)
        if cached_data is not None and page <= len(cached_data):   
            return {
                'from_cache': True,
                'pages': cached_data,
                'nextPageNumber':self.get_next_page_number(len(cached_data))
            }

        # fetch the first page if there's no cached data
        if cached_data is None and page == 1:
            data = self.get_data(1)
            cache.set(self.cache_key, [data])
            return data
        
        # fetch the page if there's no cached data and it's not the first page
        if cached_data is None and page > 1:
            data = self.get_data(page)
            return data
        
        # Add the new fetched page to the cached data        
        if cached_data is not None and page > len(cached_data):
            data = self.get_data(page) # get page data
            cache.set(self.cache_key, cached_data + [data]) # add it to existing pages
            return data
        
                
    def get_data(self, page:int):
        date_range = self.enhanced_pages.get(page)
        products = ProductSerializer(self.user.products.filter(date__date__range=(date_range[0], date_range[1]), **self.extra_filters), many=True).data
        records = groupByDate(products)
        return {
        'page': page,
        'from_cache': False,
        'records': records, 
        'nextPageNumber':self.get_next_page_number(page)
        }
        
    def get_next_page_number(self, current_page_number: int) -> int | None:
        if current_page_number < self.get_total_pages():
            return current_page_number + 1
        return None
        
        
    