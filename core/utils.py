from .serializers import ProductSerializer
from .datechecker import get_total, datefromisoformat, DateRangePaginator
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required as lr 
from django.core.cache import cache
import pandas as pd
from .models import Settings, WeeklySpending, Product, MonthlySpending
from django.db.models import Min
from authentication.models import User
from collections.abc import Callable
from django.http import HttpRequest
from datetime import datetime, date, timedelta
from urllib.parse import quote 
from core.encryption import EncryptionHelper
from django.conf import settings
from django.core.cache import cache
from typing import Optional, Any

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

def get_products_in_the_last_year(user: User) -> list[dict]:
    products = cache.get(f'products-in-last-year-{user.username}')
    if products is None:
        products = ProductSerializer(user.products.filter(date__gte=datetime.today() - timedelta(days=365), date__lte=datetime.today()), many=True).data
        cache.set(f'products-in-last-year-{user.username}', products)
    return products
        

def encryptAllProducts():
    for product in Product.objects.all(): 
        product.save() # saving indirectly encrypts the products
        
def decryptAllProducts():
    encryption_helper = EncryptionHelper(key=settings.ENCRYPTION_KEY)
    print('Decrypting all products...')
    for product in Product.objects.all():
        product.name = encryption_helper.decrypt(product.name)
        product.description = encryption_helper.decrypt(product.description)
        product.save()
    print('All products decrypted successfully.')


class EventManager:
    PRODUCT_UPDATED = 0
    CUSTOM_NAME_UPDATED = 1

class EventEmitter:
    def __init__(self):
        self._events = {}

    def on(self, event_name:str | int, callback: Callable):
        """Register an event listener for a specific event."""
        if event_name not in self._events:
            self._events[event_name] = []
        self._events[event_name].append(callback)

    def off(self, event_name:str | int, callback:Callable):
        """Remove an event listener for a specific event."""
        if event_name in self._events:
            self._events[event_name] = [cb for cb in self._events[event_name] if cb != callback]

    def emit(self, event_name:str | int, *args, **kwargs):
        """Trigger an event and call all registered listeners."""
        if event_name in self._events:
            for callback in self._events[event_name]:
                callback(*args, **kwargs)

    def once(self, event_name: str | int, callback: Callable):
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
    cm = CacheManager(request.user.username)
    cm.delete_records()
    cm.delete_enhanced_pages()
    category = kwargs.get('category')
    if category:
        cm.delete_records(category.get('name'))
        cm.delete_enhanced_pages(category.get('name'))

def updateWeeklySpendingData(request: HttpRequest, **kwargs):
    user = request.user
    dates = kwargs.get('dates')
    if dates is not None:
        settings = getSettings(user)
        if settings.populated_weekly_spending:
            for date in dates:
                WeeklySpending.update_weekly_spending(user, date)

def updateMonthlySpendingData(request: HttpRequest, **kwargs):
    user = request.user
    dates = kwargs.get('dates')
    if dates is not None:
        settings = getSettings(user)
        if settings.populated_monthly_spending:
            for date in dates:
                MonthlySpending.update_monthly_spending(user, date)


emitter = EventEmitter() # global event emitter
em = EventManager()
emitter.on(em.PRODUCT_UPDATED, deleteQuickStatsFromCache)
emitter.on(em.PRODUCT_UPDATED, deleteExpenditureRecordsFromCache)
emitter.on(em.PRODUCT_UPDATED, deleteAllProductsFromCache)
emitter.on(em.PRODUCT_UPDATED, updateWeeklySpendingData)
emitter.on(em.PRODUCT_UPDATED, updateMonthlySpendingData)
emitter.on(em.CUSTOM_NAME_UPDATED, deleteQuickStatsFromCache)
class ExpensePaginator:
    def __init__(
        self, request:HttpRequest,
        cache_key: str | None = None,
        number_of_days=7,
        category_name:str | None = None,
        extra_filters: dict | None = None,
        date_range: tuple | None = None
    ):
        """ get the relevant dates (dates where things were actually purchased) """
        if not extra_filters:
            extra_filters = {}
        if not date_range:
            date_range = (request.user.date_joined.date(), datetime.today().date())
        
        self.date_range = date_range
        self.user = request.user
        self.extra_filters = extra_filters
        self.category_name = category_name
        self.specific_category = category_name is not None
        self.number_of_days = number_of_days
        self.cache_key = cache_key
        self.enhanced_pages = self.get_enhanced_pages()

    def page_enhancer_algorithm(self, relevant_dates:list):
        enhanced_pages = {} 
        if relevant_dates:
            paginator = DateRangePaginator(
            relevant_dates[-1],
            relevant_dates[0],
            self.number_of_days,
            reverse=True)
            page = 1 
            new_page_number = 0
            i = 0  # to index the dates
            date = relevant_dates[i]
            while i < len(relevant_dates):
                current_date_range = sorted(paginator.get_date_range(page))
                if current_date_range[0] <= date <= current_date_range[1]:
                    new_page_number += 1
                while current_date_range[0] <= date <= current_date_range[1]:
                    if enhanced_pages.get(new_page_number) is None:
                        enhanced_pages[new_page_number] = current_date_range
                    i += 1
                    if i < len(relevant_dates):
                        date = relevant_dates[i]
                    else:
                        break
                page += 1
        return enhanced_pages

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
            relevant_dates = self.user.products.filter(
                category__name=self.category_name,
                date__date__range=self.date_range
            ).values('date').annotate(min_date=Min('date__date')).values_list('min_date', flat=True)
            relevant_dates = list(sorted(relevant_dates, reverse=True))
        else: # if no category is specified, we need to filter by all products
            if self.cache_key: # ! FIX: monthly pagination also uses this part of the code and the cache will mess with that
                pages = cache.get(f'enhanced-pages-{self.user.username}') # check the cache if it already exist
            else:
                pages = None
            if pages:
                return pages
            relevant_dates = self.user.products.filter(
                date__date__range=self.date_range
            ).values('date').annotate(min_date=Min('date__date')).values_list('min_date', flat=True)
            relevant_dates = list(sorted(relevant_dates, reverse=True))

        enhanced_pages = self.page_enhancer_algorithm(relevant_dates)
        cm = CacheManager(self.user.username)
        if self.specific_category:
            cm.set_enhanced_pages(enhanced_pages, self.category_name)
        else:
            if self.cache_key:
                cm.set_enhanced_pages(enhanced_pages)
        return enhanced_pages
                
                
    def get_total_pages(self):
        return len(self.enhanced_pages)
                
            
        
    def get_page(self, page: int):
        # cached data for all is just a list of pages. [{}, {}, {}, ]
        cached_data: list[dict] | None = cache.get(self.cache_key) if self.cache_key else None
        if cached_data is not None and page <= len(cached_data):   
            return {
                'from_cache': True,
                'pages': cached_data,
                'nextPageNumber':self.get_next_page_number(len(cached_data))
            }

        # fetch the first page if there's no cached data
        if cached_data is None and page == 1:
            data = self.get_data(1)
            if self.cache_key:
                cache.set(self.cache_key, [data])
            return data
        
        # fetch the page if there's no cached data and it's not the first page
        if cached_data is None and page > 1:
            data = self.get_data(page)
            return data
        
        # Add the new fetched page to the cached data        
        if cached_data is not None and page > len(cached_data):
            data = self.get_data(page) # get page data
            if self.cache_key:
                cache.set(self.cache_key, cached_data + [data]) # add it to existing pages
            return data
        
                
    def get_data(self, page:int):
        date_range = self.enhanced_pages.get(page)
        products = ProductSerializer(
            self.user.products.filter(
                date__date__range=(date_range[0], date_range[1]),
                **self.extra_filters),
            many=True).data if date_range else []
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


class CacheKeyManager:
    """Centralized cache key management to prevent typos and ensure consistency"""
    
    # Key patterns as class constants
    ENHANCED_PAGES = "enhanced-pages-{username}"
    CATEGORY_ENHANCED_PAGES = "{category_name}-enhanced-pages-{username}"
    RECORDS = "records-{username}"
    CATEGORY_RECORDS = "{category_name}-records-{username}"
    ACTIVITY_CALENDAR = "activity-calendar-{username}"
    WEEKLY_STATS = "weekly-stats-{username}"
    MONTHLY_STATS = "monthly-stats-{username}"
    
    @classmethod
    def enhanced_pages(cls, username: str) -> str:
        """Generate key for enhanced pages cache"""
        return cls.ENHANCED_PAGES.format(username=username)
    
    @classmethod
    def category_enhanced_pages(cls, category_name: str, username: str) -> str:
        """Generate key for category-specific enhanced pages cache"""
        return cls.CATEGORY_ENHANCED_PAGES.format(
            category_name=quote(category_name), 
            username=username
        )
    
    @classmethod
    def records(cls, username: str) -> str:
        """Generate key for records cache"""
        return cls.RECORDS.format(username=username)
    
    @classmethod
    def category_records(cls, category_name: str, username: str) -> str:
        """Generate key for category-specific records cache"""
        return cls.CATEGORY_RECORDS.format(
            category_name=quote(category_name), 
            username=username
        )
    
    @classmethod
    def activity_calendar(cls, username: str) -> str:
        """Generate key for activity calendar cache"""
        return cls.ACTIVITY_CALENDAR.format(username=username)
    
    @classmethod
    def weekly_stats(cls, username: str) -> str:
        """Generate key for weekly stats cache"""
        return cls.WEEKLY_STATS.format(username=username)
    
    @classmethod
    def monthly_stats(cls, username: str) -> str:
        """Generate key for monthly stats cache"""
        return cls.MONTHLY_STATS.format(username=username)
        

class CacheManager:
    """High-level cache operations with key management"""
    
    def __init__(self, username: str):
        self.username = username
        self.keys = CacheKeyManager()
    
    def get_activity_calendar(self):
        key = self.keys.activity_calendar(self.username)
        return cache.get(key)
    
    def set_activity_calendar(self, data:Any):
        key = self.keys.activity_calendar(self.username)
        cache.set(key, data)
    
    def get_enhanced_pages(self, category_name: Optional[str] = None) -> Any:
        """Get enhanced pages from cache"""
        if category_name:
            key = self.keys.category_enhanced_pages(category_name, self.username)
        else:
            key = self.keys.enhanced_pages(self.username)
        return cache.get(key)
    
    def set_enhanced_pages(self, data: Any, category_name: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """Set enhanced pages in cache"""
        if category_name:
            key = self.keys.category_enhanced_pages(category_name, self.username)
        else:
            key = self.keys.enhanced_pages(self.username)
        cache.set(key, data, timeout)
    
    def delete_enhanced_pages(self, category_name: Optional[str] = None) -> None:
        """Delete enhanced pages from cache"""
        if category_name:
            key = self.keys.category_enhanced_pages(category_name, self.username)
        else:
            key = self.keys.enhanced_pages(self.username)
        cache.delete(key)
    
    def get_records(self, category_name: Optional[str] = None) -> Any:
        """Get records from cache"""
        if category_name:
            key = self.keys.category_records(category_name, self.username)
        else:
            key = self.keys.records(self.username)
        return cache.get(key)
    
    def set_records(self, data: Any, category_name: Optional[str] = None, timeout: Optional[int] = None) -> None:
        """Set records in cache"""
        if category_name:
            key = self.keys.category_records(category_name, self.username)
        else:
            key = self.keys.records(self.username)
        cache.set(key, data, timeout)
    
    def delete_records(self, category_name: Optional[str] = None) -> None:
        """Delete records from cache"""
        if category_name:
            key = self.keys.category_records(category_name, self.username)
        else:
            key = self.keys.records(self.username)
        cache.delete(key)
    
    def clear_category_cache(self, category_name: str) -> None:
        """Clear all cache entries for a specific category"""
        self.delete_enhanced_pages(category_name)
        self.delete_records(category_name)
    
    def get_weekly_stats(self) -> Any:
        """Get weekly stats from cache"""
        key = self.keys.weekly_stats(self.username)
        return cache.get(key)
    
    def set_weekly_stats(self, data: Any, timeout: Optional[int] = None) -> None:
        """Set weekly stats in cache"""
        key = self.keys.weekly_stats(self.username)
        cache.set(key, data, timeout)
    
    def delete_weekly_stats(self) -> None:
        """Delete weekly stats from cache"""
        key = self.keys.weekly_stats(self.username)
        cache.delete(key)
    
    def get_monthly_stats(self) -> Any:
        """Get monthly stats from cache"""
        key = self.keys.monthly_stats(self.username)
        return cache.get(key)
    
    def set_monthly_stats(self, data: Any, timeout: Optional[int] = None) -> None:
        """Set monthly stats in cache"""
        key = self.keys.monthly_stats(self.username)
        cache.set(key, data, timeout)
    
    def delete_monthly_stats(self) -> None:
        """Delete monthly stats from cache"""
        key = self.keys.monthly_stats(self.username)
        cache.delete(key)