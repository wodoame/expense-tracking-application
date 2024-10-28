from django.shortcuts import render, redirect, HttpResponse
from django.views import View
from datetime import datetime, timedelta
from .models import Product, Category
import core.datechecker as dc 
from django.core.paginator import Paginator 
from django.db.models import Count
from .forms import AddProductForm
from .serializers import ProductSerializer, CategorySerializer
from django.contrib import messages 
import json
import pandas as pd
from .stats import Context, WeeklyStats

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

class Dashboard(View):
    def get(self, request):
        products = Product.objects.all() 
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        statContext = Context(WeeklyStats(products))
        stats = statContext.apply() 
        today = [product for product in products if product.date.date() == dateToday]
        yesterday = [product for product in products if product.date.date() == dateYesterday]
        todayTotal = dc.get_total(today)
        yesterdayTotal = dc.get_total(yesterday)
        serializer = ProductSerializer(products, many=True)
        cateogorySerializer = CategorySerializer(Category.objects.all(), many=True) 
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
            'totalSpentThisWeek': stats[0],
            'totalSpentLastWeek': stats[1],
            'highestWeeklySpending': stats[2],
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal,
            'products': serializer.data, 
            'categories': cateogorySerializer.data 
        }
        return render(request, 'core/pages/dashboard.html', context)
    
    def post(self, request):
        if request.GET.get('edit'): 
            return self.handle_edit_product(request)
        if request.GET.get('delete'):
            return self.handle_delete_product(request)
        return self.handle_add_product(request)
        
    def check_category(self, request):
        categoryId = request.POST.get('category')
        
        if categoryId != '' and int(categoryId) == 0:
            category = Category.objects.create(name=request.POST.get('newCategoryName'))
            postDict = request.POST.dict()
            postDict['category'] = category.id
            return postDict
        return request.POST
    
        
    def handle_edit_product(self, request):
        productId = request.POST.get('id')
        try:
            instance = Product.objects.get(id=productId)
            form = AddProductForm(self.check_category(request), instance=instance)
            cedis = request.POST.get('cedis')
            pesewas = request.POST.get('pesewas')
            price = float(cedis + '.' + pesewas)
            if form.is_valid():
                instance = form.save(commit=False)
                instance.price = price
                form.save() 
                messages.success(request, 'Product edited successfully')
            else: 
                errors = form.errors.get_json_data()
                print(errors) 
        except Product.DoesNotExist:
            messages.error(request, 'Product has been deleted')
        return redirect(request.META.get('HTTP_REFERER'))
    
    from django.http import HttpRequest
    def handle_add_product(self, request: HttpRequest):
        form = AddProductForm(self.check_category(request))
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = float(cedis + '.' + pesewas)
        if form.is_valid():
            print(form.cleaned_data)
            product = form.save(commit=False)
            product.price = price
            form.save()
            messages.success(request, 'Product added successfully')
        else: 
            errors = form.errors.get_json_data()
            print(errors)
        return redirect(request.META.get('HTTP_REFERER'))
    
    def handle_delete_product(self, request):
        productId = request.POST.get('id')
        try:
            Product.objects.get(id=productId).delete()
            messages.success(request, 'Product deleted successfully')
        except Product.DoesNotExist:
            messages.error(request, 'Product already deleted')
        return redirect(request.META.get('HTTP_REFERER'))
        
    
class ActivityCalendar(View):
    def get(self, request): 
        monthsData = dc.get_activity_in_last_year()
        context = {
            'monthsData': monthsData, 
        }
        return render(request, 'core/components/activityCalendar.html', context)

class AllExpenditures(View): 
    def get(self, request):
        products = Product.objects.all()
        categories = Category.objects.all()
        serializer = ProductSerializer(products, many=True)
        categorySerializer = CategorySerializer(categories, many=True)
        results = products.values('date__date').annotate(Count('date__date'))
        dates = [result['date__date'] for result in results] # getting only the dates
        dates.sort(reverse=True)
        records = []
        for date in dates: 
            products = Product.objects.filter(date__date=date)
            serializer2 = ProductSerializer(products, many=True)
            records.append({
                'date': date, 
                'products': serializer2.data, 
                'total':dc.get_total(products)
            })
        
        context = {
         'products':serializer.data,
         'records': records, 
         'categories': categorySerializer.data,
        }
        return render(request, 'core/pages/allExpenditures.html', context)
    
class Records(View):
    def post(self, request):
        # I'm sending the data through the request instead of calling the database again
        records = json.loads(request.POST.get('records'))
        pageNumber = request.GET.get('page')
        paginator = Paginator(records, 4)
        page = paginator.page(pageNumber)
        nextPageNumber = None
        if page.has_next(): 
            nextPageNumber = page.next_page_number()
        items = page.object_list
        context = {
            'items':items, 
            'nextPageNumber':nextPageNumber
            }
        return render(request, 'core/components/paginateExpenditures.html', context)

class Settings(View): 
    def get(self, request):
        return render(request, 'core/pages/settings.html')
    
class Test(View):
    def get(self, request): 
        context = {}
        products = ProductSerializer(Product.objects.all(), many=True).data 
        # filterDate = pd.to_datetime('2024-10-18T14:25:46.566644Z')
        # print(filterDate)
        df = pd.DataFrame(products)
        print(df)
        print('maximum amount', df.get('price').max())
        filteredDf = df['date'] > '2024-10-18T14:25:46.566644Z'
        print(filteredDf)
        return render(request, 'core/pages/test.html', context)
    
        