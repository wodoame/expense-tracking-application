from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta
from .models import Product
from .datechecker import DateChecker as dc
from django.core.paginator import Paginator 
from django.db.models import Count
from .forms import AddProductForm
from .serializers import ProductSerializer
from django.contrib import messages 
import json

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

class Dashboard(View):
    def get(self, request):
        products = Product.objects.all() 
        dateToday = datetime.today().date()
        dateYesterday = dateToday - timedelta(days=1)
        thisWeek = dc.get_week(dateToday)
        lastWeek = (thisWeek[0] - timedelta(days=7), thisWeek[1] - timedelta(days=7))
        today = [product for product in products if product.date.date() == dateToday]
        yesterday = [product for product in products if product.date.date() == dateYesterday]
        totalSpentThisWeek = dc.get_total_spent_in_week(thisWeek, products)
        totalSpentLastWeek = dc.get_total_spent_in_week(lastWeek, products)
        todayTotal = dc.get_total(today)
        yesterdayTotal = dc.get_total(yesterday)
        serializer = ProductSerializer(products, many=True)
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
            'totalSpentThisWeek': totalSpentThisWeek,
            'totalSpentLastWeek': totalSpentLastWeek,
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal,
            'products': serializer.data
        }
        return render(request, 'core/pages/dashboard.html', context)
    
    def post(self, request):
        if request.GET.get('edit'): 
            return self.handle_edit_product(request)
        if request.GET.get('delete'):
            return self.handle_delete_product(request)
        return self.handle_add_product(request)
        
    
    def handle_edit_product(self, request):
        productId = request.POST.get('id')
        try:
            instance = Product.objects.get(id=productId)
            form = AddProductForm(request.POST, instance=instance)
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
    
    def handle_add_product(self, request):
        form = AddProductForm(request.POST)
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = float(cedis + '.' + pesewas)
        if form.is_valid():
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
        serializer = ProductSerializer(products, many=True)
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
         'records': records
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

class Test(View):
    def get(self, request): 
        return render(request, 'core/components/blank.html')
    
        