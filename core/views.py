from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, Category
import core.datechecker as dc 
from .forms import *
from .serializers import * 
from django.contrib import messages 
import pandas as pd
from .stats import * 
from .utils import *
from django.utils import timezone
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.http import JsonResponse
from urllib.parse import urlparse, unquote, quote
from django.core.cache import cache
from .placeholder_views import AllExpenditures
import re
from .user_settings_schemas import * 
from api.utils import indexEventEmitter
from api.views import Search as APISearch
from django.forms.forms import ValidationError

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

class Dashboard(View):
    def get(self, request):
        user = request.user
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        products = ProductSerializer(user.products.filter(date__date__gte=dateYesterday), many=True).data
        today = []
        yesterday = []
        for product in products:
            if dc.datefromisoformat(product.get('date')).date() == dateToday:
                today.append(product)
            else:
                yesterday.append(product)
        todayTotal = dc.get_total(today)
        yesterdayTotal = dc.get_total(yesterday)
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal,
        }
        return render(request, 'core/implementations/dashboard.html', context)
    
    def post(self, request):
        if request.GET.get('edit'): 
            return self.handle_edit_product(request)
        if request.GET.get('delete'):
            return self.handle_delete_product(request)
        return self.handle_add_product(request)
        
    def check_category(self, request):
        categoryId = request.POST.get('category') 
        if categoryId is None:
            return request.POST     
        if categoryId != '' and int(categoryId) == 0:
            category = Category.objects.create(name=request.POST.get('newCategoryName'), user=request.user)
            postDict = request.POST.dict()
            postDict['category'] = category.id
            return postDict
        return request.POST
    
    def format_price(self, cedis, pesewas):
        if len(pesewas) == 1:
            pesewas = '0' + pesewas
        price = float(cedis + '.' + pesewas)
        return price 
    
        
    def handle_edit_product(self, request):
        print(request.POST)
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            form = AddProductForm(self.check_category(request), instance=product)
            cedis = request.POST.get('cedis')
            pesewas = request.POST.get('pesewas')
            price = self.format_price(cedis, pesewas)
            parsedDate = datetime.strptime(request.POST.get('new-date'), '%Y-%m-%d')
            date = dc.datefromisoformat(request.POST.get('date')).date()
            dates = [date]
            if form.is_valid():
                product = form.save(commit=False)
                product.price = price
                product.user = request.user
                if parsedDate.date() != product.date.date():
                    product.date = timezone.make_aware(parsedDate, timezone.get_current_timezone())
                    dates.append(parsedDate.date())
                form.save() 
                messages.success(request, 'Product edited successfully')
                referer = request.META.get('HTTP_REFERER')
                path = urlparse(referer).path
                if referer is not None and re.match(r'^/categories/[^/]+/$', path):
                    segments = path.split('/')
                    categoryName = unquote(list(filter(lambda x: x != '', segments)).pop())
                    products = ProductSerializer(request.user.products.filter(category__name=categoryName, date__date__in=dates), many=True).data
                    items = [record2(date, products) for date in dates] 
                else: 
                    items = [record(date, request) for date in dates]
                context = {
                    'items':items, 
                    'showToast':True,
                    'edited':True
                }    
                emitter.emit('products_updated', request, dates=dates) # for editing a product, two different weeks may be affected
                serializedProduct =  ProductSerializer(product).data
                category:dict | None = serializedProduct.get('category')
                if category is not None:
                    cache.delete(f"{quote(category.get('name'))}-records-{request.user.username}")
                    cache.delete(f"{quote(category.get('name'))}-enhanced-pages-{request.user.username}")

                indexEventEmitter.emit('product_updated', serializedProduct)
                return render(request, 'core/components/paginateExpenditures.html', context) 
            else: 
                errors = form.errors.get_json_data()
                print(errors) 
        except Product.DoesNotExist:
            messages.error(request, 'Product has been deleted')
        return redirect(request.META.get('HTTP_REFERER'))
    
    def handle_add_product(self, request: HttpRequest):
        print(request.POST)
        form = AddProductForm(self.check_category(request))
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = self.format_price(cedis, pesewas)
        parsedDate = datetime.strptime(request.POST.get('date'), '%Y-%m-%d')
        dateToday = datetime.today().date()
        if form.is_valid():
            product = form.save(commit=False)
            product.price = price
            product.user = request.user
            if parsedDate.date() != dateToday:
                product.date = timezone.make_aware(parsedDate, timezone.get_current_timezone())
            form.save()
            emitter.emit('products_updated', request, dates=[product.date.date()])
            serializedProduct =  ProductSerializer(product).data
            indexEventEmitter.emit('product_updated', serializedProduct)
            category:dict | None = serializedProduct.get('category')
            if category is not None:
                cache.delete(f"{quote(category.get('name'))}-records-{request.user.username}")
                cache.delete(f"{quote(category.get('name'))}-enhanced-pages-{request.user.username}") 
            messages.success(request, 'Product added successfully')
        else: 
            errors = form.errors.get_json_data()
            print(errors)
        referer = request.META.get('HTTP_REFERER')
        path = urlparse(referer).path
        if path == '/all-expenditures/':
            return redirect('/components/records/?page=1&addProduct=1')
        if path == '/dashboard/':
            return redirect('implemented-dashboard')
        if path == '/categories/':
            return redirect('implemented-categories')
        if referer is not None and re.match(r'^/categories/[^/]+/$', path):
           segments = path.split('/')
           categoryName = quote(unquote(list(filter(lambda x: x != '', segments)).pop()))
           return redirect(f'/components/records/?page=1&addProduct=1&oneCategory=1&categoryName={categoryName}')
        return render(request, 'core/components/toastWrapper/toastWrapper.html', {})
        
    
    def handle_delete_product(self, request):
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            serializedProduct =  ProductSerializer(product).data
            category:dict | None = serializedProduct.get('category')
            product.delete()
            indexEventEmitter.emit('product_updated', serializedProduct, method='delete')
            if category is not None:
                cache.delete(f"{quote(category.get('name'))}-records-{request.user.username}")
                cache.delete(f"{quote(category.get('name'))}-enhanced-pages-{request.user.username}")
                
            messages.success(request, 'Product deleted successfully')
            date = dc.datefromisoformat(request.POST.get('date')).date() 
            referer = request.META.get('HTTP_REFERER')
            path = urlparse(referer).path
            if referer is not None and re.match(r'^/categories/[^/]+/$', path):
                segments = path.split('/')
                categoryName = unquote(list(filter(lambda x: x != '', segments)).pop())
                products = ProductSerializer(request.user.products.filter(category__name=categoryName, date__date=date), many=True).data
                items = [record2(date, products)] 
            else:
                items = [record(date, request)]
            context = {
                'items':items,
                'showToast':True,
            }
            emitter.emit('products_updated', request, dates=[date])
            if not items[0].get('products'):
                return render(request, 'core/components/toastWrapper/toastWrapper.html', context) # return toastWrapper.html so that the success message will be displayed
            return render(request, 'core/components/paginateExpenditures.html', context) 
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')

class ActivityCalendar(View):
    def get(self, request): 
        response = cache.get(f'activity-calendar-{request.user.username}')
        if response:
            return response
        monthsData = dc.get_activity_in_last_year(request)
        context = {
            'monthsData': monthsData, 
        }
        response = render(request, 'core/components/activityCalendar.html', context)
        cache.set(f'activity-calendar-{request.user.username}', response)
        return response

# @login_required    
class Records(View):
    def get(self, request): 
        """
         query parameters:
            - page: the page number to be displayed
            - oneCategory: if True, only records for the specified category will be displayed
            - categoryName: the name of the category to be displayed
            - addProduct: if True, a toast will be displayed to indicate that a product has been added
        """
        records = []
        nextPageNumber = None
        user = request.user 
        if request.GET.get('oneCategory'):
            categoryName = unquote(request.GET.get('categoryName'))
            if categoryName != 'None':
                paginator = EnhancedExpensePaginator(
                    request,
                    cache_key=f'{quote(categoryName)}-records-{user.username}', 
                    specific_category=True, 
                    category_name=categoryName, 
                    extra_filters={'category__name': categoryName}
                    ) 
                page = int(request.GET.get('page'))
                pageData = paginator.get_page(page) # e.g pageData -> {'nextPageNumber': 2, 'records': [], 'from_cache': False}
                nextPageNumber = pageData.get('nextPageNumber')      
                print(nextPageNumber)
                if pageData.get('from_cache'):
                    return self.cache_response(pageData)
                records = pageData.get('records')
            else: 
                products = ProductSerializer(user.products.filter(category=None), many=True).data
                records = groupByDate(products)
        elif request.GET.get('week_id'):
            week_id = request.GET.get('week_id')
            return self.get_week(request, week_id)
        else:
            paginator = EnhancedExpensePaginator(
                    request,
                    cache_key=f'records-{request.user.username}', 
                    ) 
            page = int(request.GET.get('page'))
            pageData = paginator.get_page(page)
            nextPageNumber = pageData.get('nextPageNumber')
            print(nextPageNumber)
            if pageData.get('from_cache'):
                return self.cache_response(pageData)                
    
            records = pageData.get('records')
        context = {
            'items':records, 
            'nextPageNumber':nextPageNumber,
            'seeProductsPage': request.GET.get('addProduct')
            }
        context.update(getRecordSkeletonContext())
        return render(request, 'core/components/paginateExpenditures.html', context)
    
    def get_week(self, request: HttpRequest, week_id: int):
        user = request.user
        spending_data = WeeklySpending.objects.get(id=week_id)
        products = ProductSerializer(
            Product.objects.filter(date__date__range=(spending_data.week_start, spending_data.week_end), user=user),
            many=True).data
        records = groupByDate(products)
        context = {
            'items': records, 
        }
        return render(request, 'core/components/paginateExpenditures.html', context)
    
            

    def generate_html_from_cache(self, pages: list[dict], context:dict):
        html = ''
        for page in pages:
            html += render_to_string('core/components/paginateExpenditures.html', {'items': page.get('records')})
        if context.get('nextPageNumber') is not None:
            html += render_to_string('core/components/paginator.html', context)
        return HttpResponse(html)
    
    def cache_response(self, pageData: list[dict]):
        pages = pageData.get('pages')
        nextPageNumber = pageData.get('nextPageNumber')
        context = {'nextPageNumber': nextPageNumber}
        context.update(getRecordSkeletonContext())
        return self.generate_html_from_cache(pages, context)
    
# @login_required
class Settings(View): 
    def get(self, request):
        return render(request, 'core/pages/settings.html')


class Test(View):
    def get(self, request):
        context = {}
        use_date = request.user.products.last().date
        res = MonthlySpending.update_monthly_spending(request.user, use_date)
        print(res)
        return render(request, 'core/pages/test.html', context)
    
    def post(self, request): 
       pass

class Routes(View): 
    def get(self, request): 
        context = {}
        if request.GET.get('all'):
            return JsonResponse(
                {
                  '/dashboard/': render_to_string('core/placeholders/dashboardSkeleton.html', getRecordSkeletonContext()),
                  '/all-expenditures/': render_to_string('core/placeholders/allExpendituresSkeleton.html', getRecordSkeletonContext()),
                  '/categories/': render_to_string('core/placeholders/categoriesPageSkeleton.html', getCategoriesSkeletonContext()),
                  '/statSummarySkeleton/': render_to_string('core/components/statSummarySkeleton.html'), 
                  '/categories/category-name/': render_to_string('core/placeholders/seeProductsSkeleton.html',getRecordSkeletonContext()),
                  'seeProductsSkeleton': render_to_string('core/placeholders/seeProductsSkeleton2.html',getRecordSkeletonContext()),
                  '/search/': render_to_string('core/components/staticRecordSkeleton2.html', getRecordSkeletonContext()),
                  'viewWeekSkeleton': render_to_string('core/placeholders/allExpendituresSkeleton.html', getRecordSkeletonContext()),
                }
            )
        return render(request, 'core/components/blank.html', context)


class Categories(View):
    def get(self, request):
        user = request.user
        categories = CategorySerializerWithMetrics(user.categories.all(), many=True).data
        productsWithNoCategory = ProductPriceSerializer(user.products.filter(category=None), many=True).data
        df = pd.DataFrame(productsWithNoCategory)
        metrics = {
            "product_count": 0, 
            "total_amount_spent": 0
        }
        if not df.empty:
            # NOTE: explicitly convert to the respective data types since the original result from pandas is an object
            metrics['product_count'] = int(df.get('name').count())
            metrics['total_amount_spent'] = float(df.get('price').sum())
        categories.append(
            {
                "name": "None",
                "metrics": metrics
            }
        )
        categories.sort(key=lambda x:x['metrics']['total_amount_spent'], reverse=True)
        context = {
            'categories': categories
        }
        return render(request, 'core/implementations/categories.html', context)
    
    def post(self, request):
        if request.GET.get('edit'):
            return self.handle_edit_category(request)
        if request.GET.get('delete'):
            return self.handle_delete_category(request)
        return self.handle_add_category(request)
       
    def handle_add_category(self, request): 
        user = request.user
        form = AddCategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = user
            category.save()
            messages.success(request, 'Category added successfully')
            emitter.emit('products_updated', request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return redirect('implemented-categories')
    
    def handle_edit_category(self, request): 
        categoryId = request.POST.get('id')
        category = Category.objects.get(id=categoryId)
        form = AddCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            messages.success(request, 'Category edited successfully')
            emitter.emit('products_updated', request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return redirect('implemented-categories')
    
    def handle_delete_category(self, request): 
        categoryId = request.POST.get('id')
        try:
            Category.objects.get(id=categoryId).delete()
            messages.success(request, 'Category deleted successfully')
            emitter.emit('products_updated', request) # some products may still be associated with the deleted category so the cache must be cleared
        except Product.DoesNotExist:
            messages.error(request, 'Category already deleted')
        return redirect('implemented-categories')
    
class StatSummary(View):
    def get(self, request):
        stats = None
        user = request.user
        if request.GET.get('type') == 'weekly':
            stats = cache.get(f'weekly-stats-{user.username}')
            if not stats:
                stats = Context(WeeklyStats(user)).apply()
                cache.set(f'weekly-stats-{user.username}', stats)
        if request.GET.get('type') == 'monthly':
            stats = cache.get(f'monthly-stats-{user.username}')
            if not stats:
                stats = Context(MonthlyStats(user)).apply()
                cache.set(f'monthly-stats-{user.username}', stats)  
        print(stats)
        context = {
            'stats':stats
        }
        return render(request, 'core/components/statSummary.html', context)
class Search(View):
    def get(self, request):
        return render(request, 'core/pages/search-results.html')
        
class SearchResults(View):
    def get(self, request):
        print(request.GET)
        query = request.GET.get('query').strip()
        user = request.user 
        data = APISearch.search_products(query, user)
        context = {
            'results': data.get('results')
        }
        return render(request, 'core/components/searchResults.html', context)   