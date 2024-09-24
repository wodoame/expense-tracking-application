from django.shortcuts import render, redirect
from django.urls import reverse

from django.views import View
from .forms import AddProductForm
from datetime import datetime, timedelta 
from .models import Product
from .datechecker import DateChecker as dc

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
            }     
        
        return render(request, 'dashboard.html', context)
    
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
    
    def get_total_cost(self, items):
        totalCost = 0
        for item in items:
            totalCost += item.price
        return totalCost 
            