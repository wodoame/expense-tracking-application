from django.shortcuts import render, redirect
from django.views import View
from datetime import datetime, timedelta
from .models import Product
from .datechecker import DateChecker as dc

class RedirectView(View):
    def get(self, request):
        return redirect('dashboard')

class Dashboard(View):
    def get(self, request):
        products = Product.objects.all() 
        # print(products.first())
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
        context = {
            'dateToday':dateToday, 
            'dateYesterday':dateYesterday, 
            'today': today, 
            'totalSpentThisWeek': totalSpentThisWeek,
            'totalSpentLastWeek': totalSpentLastWeek,
            'yesterday':yesterday,
            'todayTotal':todayTotal,
            'yesterdayTotal':yesterdayTotal 
        }
        return render(request, 'core/pages/dashboard.html', context)

class ActivityCalendar(View):
    def get(self, request): 
        monthsData = dc.get_activity_in_last_year()
        context = {
            'monthsData': monthsData, 
        }
        return render(request, 'core/components/activityCalendar.html', context)
class Test(View):
    def get(self, request): 
        result = dc.get_activity_in_last_year()
        print(result)
        return render(request, 'core/pages/test.html')
    
        