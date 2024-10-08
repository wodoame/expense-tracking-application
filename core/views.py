from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.views import View
from .forms import AddProductForm
from datetime import datetime, timedelta 
from .models import Product
from .datechecker import DateChecker as dc
from django.db.models import Count, Sum
from .serializers import ProductSerializer
from django.core.paginator import Paginator, EmptyPage 
from django.core.cache import cache

class RedirectView(View):
    def get(self, request): 
        return redirect('dashboard')

class Dashboard(View): 
    def get(self, request, **kwargs):
        products = Product.objects.all()
        dateToday = datetime.today().date()
        dateYesterday = datetime.today().date() - timedelta(days=1)
        thisWeek = dc.get_week(dateToday)
        lastWeek = (thisWeek[0] - timedelta(weeks=1), thisWeek[1] - timedelta(weeks=1))
        today = [item for item in products if item.date.date() == dateToday]
        yesterday = [item for item in products if item.date.date() == dateYesterday]
        spentThisWeek = dc.spent_in_week(thisWeek, products)
        spentLastWeek = dc.spent_in_week(lastWeek, products)

        serializer = ProductSerializer(today + yesterday, many=True)
        serializedData = serializer.data
        context = {
            'today': today,
            'yesterday': yesterday,
            'dateToday': dateToday,
            'dateYesterday': dateYesterday,
            'todayTotal': self.get_total_cost(today), 
            'yesterdayTotal': self.get_total_cost(yesterday), 
            'successful': kwargs.get('successful'),
            'spentThisWeek': spentThisWeek,
            'spentLastWeek': spentLastWeek,
            'serializedData':serializedData
            }     
        
        
        return render(request, 'pages/dashboard.html', context)
    
    def post(self, request):
        form = AddProductForm(request.POST)
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = float(cedis + '.' + pesewas)
        if form.is_valid():
            print(form.cleaned_data)
            product = form.save(commit=False)
            product.price = price
            form.save()
        else: 
            print(form.errors.get_json_data())
        return self.get(request, successful=True)
    
    # I could use aggregation instead (But this works already so no problem)
    def get_total_cost(self, items):
        totalCost = 0
        for item in items:
            totalCost += item.price
        return totalCost 
    
class AllExpenditures(View): 
    def get(self, request):
        context = {'serializedData': ProductSerializer(Product.objects.all(), many=True).data }
        return render(request, 'pages/all-expenditures.html', context)
    
class Records(View):
    def get(self, request): 
        pageNumber = request.GET.get('page')
        records = cache.get('records')
        if not records:
            results = Product.objects.values('date__date').annotate(Count('date__date')) # dates and number of items bought on that day
            dates = [result['date__date'] for result in results] # getting only the dates
            records = []
            dates.sort(reverse=True) 
            for date in dates:
                products = Product.objects.filter(date__date=date)
                records.append({
                    'date': date, 
                    'products': products, 
                    'total':products.aggregate(total=Sum('price')).get('total')
                })
        
            cache.set('records', records)
            
        paginator = Paginator(records, 2)
        page = paginator.page(pageNumber)
        nextPageLink = None
        if page.has_next():
            nextPageLink = f'/components/records/?page={page.next_page_number()}' 
        items = page.object_list
        return render(request, 'components/paginate-expenditures.html', {'records': items, 'nextPageLink': nextPageLink})
            
        
    
    
    
    
# TODO: the delete and edit button functionality
# TODO: try to write a bash script to start the server and the tailwind build process
# .aggregate() is used to perform some calculations across the whole queryset

class AcitivityCalendar(View): 
    # not essential to be recomputing this view everytime 
    def get(self, request): 
        response = cache.get('activityCalendar')
        if response:
            return response
        
        monthsData = dc.get_activity_in_last_year(Product.objects.all())
        context = {
            'monthsData': monthsData
        }
        
        response = render(request, 'components/activityCalendar.html', context)
        cache.set('activityCalendar', response)
        return response 


class DeleteProduct(View): 
    def post(self, request): 
        id = request.POST.get('id')
        Product.objects.get(id=id).delete()
        return redirect(request.META['HTTP_REFERER'])

class Test(View): 
    def get(self, request):
        return render(request, 'pages/test.html')