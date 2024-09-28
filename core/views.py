from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from .forms import AddProductForm
from datetime import datetime, timedelta 
from .models import Product
from .datechecker import DateChecker as dc
from django.db.models import Count, Sum
from .serializers import ProductSerializer

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
        print(request.POST)
        form = AddProductForm(request.POST)
        cedis = request.POST.get('cedis')
        pesewas = request.POST.get('pesewas')
        price = float(cedis + '.' + pesewas)
        print(price)
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
        # PERSONAL NOTE: It's okay if you don't remember why the code below works. I don't even fully understand it at the time of writing the code
        results = Product.objects.values('date__date').annotate(Count('date__date')) # dates and number of items bought on that day
        dates = [result['date__date'] for result in results] # getting only the dates
        records = []
        dates.sort() 
        for date in dates:
            products = Product.objects.filter(date__date=date)
            records.append({
                'date': date, 
                'products': products, 
                'total':products.aggregate(total=Sum('price')).get('total')
            })
        
        context = {'records':records }
        return render(request, 'pages/all-expenditures.html', context)
    
# TODO: the delete and edit button functionality
# TODO: try to write a bash script to start the server and the tailwind build process
# .aggregate() is used to perform some calculations across the whole queryset

class AcitivityCalendar(View): 
    def get(self, request): 
        months = (9, 8, 7, 6, 5, 4, 3, 2, 1)
        monthsData = []
        for month in months: 
            data = dc.get_calendar_data(month)
            ratios = dc.get_color_ratios(month, Product.objects.filter(date__month=month))
            lastDays, otherDays, date = data
            monthsData.append(
                {
                    'lastDays':lastDays, 
                    'ratios': ratios, 
                    'date': date
                }
            )
        
        context = {
            'monthsData': monthsData
        }
        return render(request, 'components/activityCalendar.html', context)


class DeleteProduct(View): 
    def post(self, request): 
        print(request.POST)
        id = request.POST.get('id')
        Product.objects.get(id=id).delete()
        return redirect('dashboard')

class Test(View): 
    def get(self, request): 
        # data in the last year
        
        return render(request, 'pages/test.html')