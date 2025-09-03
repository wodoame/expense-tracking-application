from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, Category
import core.datechecker as dc 
from .forms import *
from .serializers import * 
from django.contrib import messages 
from .stats import * 
from .utils import *
from django.utils import timezone
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.http import JsonResponse
from urllib.parse import urlparse, unquote, quote
import re
from .user_settings_schemas import * 
from api.views import Search as APISearch

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
                serializedProduct =  ProductSerializer(product).data
                category:dict | None = serializedProduct.get('category')
                emitter.emit(em.PRODUCT_UPDATED, request, dates=dates, category=category) # for editing a product, two different weeks may be affected
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
            serializedProduct =  ProductSerializer(product).data
            category:dict | None = serializedProduct.get('category')
            emitter.emit(em.PRODUCT_UPDATED, request, dates=[product.date.date()], category=category)
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
            return render(request, 'core/components/toastWrapper/toastWrapper.html')
        if referer is not None and re.match(r'^/categories/[^/]+/$', path):
           segments = path.split('/')
           categoryName = quote(unquote(list(filter(lambda x: x != '', segments)).pop()))
           return redirect(f'/components/records/?oneCategory=1&categoryName={categoryName}')
        return redirect('implemented-dashboard')
        
    
    def handle_delete_product(self, request):
        productId = request.POST.get('id')
        try:
            product = Product.objects.get(id=productId)
            serializedProduct =  ProductSerializer(product).data
            category:dict | None = serializedProduct.get('category')
            product.delete()
            
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
            emitter.emit(em.PRODUCT_UPDATED, request, dates=[date], category=category)
            if not items[0].get('products'):
                return render(request, 'core/components/toastWrapper/toastWrapper.html', context) # return toastWrapper.html so that the success message will be displayed
            return render(request, 'core/components/paginateExpenditures.html', context) 
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')

class ActivityCalendar(View):
    def get(self, request): 
        cm = CacheManager(request.user.username)
        response = cm.get_activity_calendar()
        if response:
            return response
        monthsData = dc.get_activity_in_last_year(request)
        context = {
            'monthsData': monthsData, 
        }
        response = render(request, 'core/components/activityCalendar.html', context)
        cm.set_activity_calendar(response)
        return response

# @login_required    
class Records(View):
    def get(self, request):
        if request.GET.get('oneCategory'):
            return self.get_category(request)
        elif request.GET.get('seeDay'):
            date = request.GET.get('date')
            return self.get_day(request, date)
        elif request.GET.get('week_id'):
            week_id = request.GET.get('week_id')
            return self.get_week(request, week_id)
        elif request.GET.get('month_id'):
            month_id = request.GET.get('month_id')
            return self.get_month(request, month_id)
        else:
            return self.get_all(request)
        
    def get_all(self, request:HttpRequest):
        paginator = ExpensePaginator(
                    request,
                    cache_key=CacheKeyManager.records(request.user.username), 
                    ) 
        page = int(request.GET.get('page') or 1)
        pageData = paginator.get_page(page)
        nextPageNumber = pageData.get('nextPageNumber')
        if pageData.get('from_cache'):
            return self.cache_response(pageData)                

        records = pageData.get('records')
        context = {
            'items':records, 
            'nextPageNumber':nextPageNumber,
        }
        context.update(getRecordSkeletonContext())
        return render(request, 'core/components/paginateExpenditures.html', context)
        
    def get_category(self, request:HttpRequest):
        user = request.user
        nextPageNumber = None
        category_name = unquote(request.GET.get('categoryName'))
        if category_name != 'None':
            paginator = ExpensePaginator(
                request,
                cache_key=CacheKeyManager.category_records(category_name, user.username), 
                category_name=category_name, 
                extra_filters={'category__name': category_name}
                ) 
            page = int(request.GET.get('page') or 1) 
            pageData = paginator.get_page(page) # e.g pageData -> {'nextPageNumber': 2, 'records': [], 'from_cache': False}
            nextPageNumber = pageData.get('nextPageNumber')      
            if pageData.get('from_cache'):
                return self.cache_response(pageData)
            records = pageData.get('records')
        else: 
            products = ProductSerializer(user.products.filter(category=None), many=True).data
            records = groupByDate(products)
        context = {
            'items': records,
            'nextPageNumber': nextPageNumber
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
    
    def get_month(self, request: HttpRequest, month_id: int):
        spending_data = MonthlySpending.objects.get(id=month_id)
        paginator = ExpensePaginator(
            request,
            date_range=(spending_data.month_start, spending_data.month_end)
        )
        page = int(request.GET.get('page') or 1)
        pageData = paginator.get_page(page)
        nextPageNumber = pageData.get('nextPageNumber')
        if pageData.get('from_cache'):
            return self.cache_response(pageData)     
        records = pageData.get('records')
        context = {
            'items': records, 
            'nextPageNumber': nextPageNumber,
            'extra_query_params': f'&month_id={month_id}'
        }
        context.update(getRecordSkeletonContext())
        return render(request, 'core/components/paginateExpenditures.html', context)
    
    def get_day(self, request: HttpRequest, date: str):
        user = request.user
        date = dc.datefromisoformat(date).date()
        products = ProductSerializer(user.products.filter(date__date=date), many=True).data
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
        # decryptAllProducts()
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
                  'viewWeekSkeleton': render_to_string('core/placeholders/seeWeekSkeleton.html', getRecordSkeletonContext()),
                  'seeDaySkeleton': render_to_string('core/placeholders/allExpendituresSkeleton.html', getRecordSkeletonContext(card_count=1)),
                  '/weeks/': render_to_string('core/placeholders/weeks.html')
                }
            )
        return render(request, 'core/components/blank.html', context)


class Categories(View):
    
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
            emitter.emit(em.PRODUCT_UPDATED, request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')
    
    def handle_edit_category(self, request): 
        categoryId = request.POST.get('id')
        category = Category.objects.get(id=categoryId)
        form = AddCategoryForm(request.POST, instance=category)
        if form.is_valid():
            category = form.save(commit=False)
            category.save()
            messages.success(request, 'Category edited successfully')
            emitter.emit(em.PRODUCT_UPDATED, request)
        else: 
            print(form.errors.get_json_data())
            messages.error(request, 'Could not add category')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')
    
    def handle_delete_category(self, request): 
        categoryId = request.POST.get('id')
        try:
            Category.objects.get(id=categoryId).delete()
            messages.success(request, 'Category deleted successfully')
            emitter.emit(em.PRODUCT_UPDATED, request) # some products may still be associated with the deleted category so the cache must be cleared
        except Product.DoesNotExist:
            messages.error(request, 'Category already deleted')
        return render(request, 'core/components/toastWrapper/toastWrapper.html')
    
class StatSummary(View):
    def get(self, request):
        stats = None
        user = request.user
        cm = CacheManager(user.username)
        if request.GET.get('type') == 'weekly':
            stats = cm.get_weekly_stats()
            if not stats:
                stats = Context(WeeklyStats(user)).apply()
                cm.set_weekly_stats(stats)
        if request.GET.get('type') == 'monthly':
            stats = cm.get_monthly_stats()
            if not stats:
                stats = Context(MonthlyStats(user)).apply()
                cm.set_monthly_stats(stats) 
        context = {
            'stats':stats, 
            'type': request.GET.get('type')
        }
        return render(request, 'core/components/statSummary.html', context)
class Search(View):
    def get(self, request):
        return render(request, 'core/pages/search-results.html')
        
class SearchResults(View):
    def get(self, request):
        print(request.GET)
        query = request.GET.get('query').lower().strip()
        page_number = int(request.GET.get('page_number', 1))
        user = request.user
        data = APISearch.search_products(query, user, page_number)
        context = {
            'results': data.get('results'), 
            'query': query,
        }
        context.update(getRecordSkeletonContext(row_count=2))
        # if request.GET.get('additional'): 
        #     return render(request, 'core/components/additionalSearchResults.html', context)
        return render(request, 'core/components/searchResults.html', context)   