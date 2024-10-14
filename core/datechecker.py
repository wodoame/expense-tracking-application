from datetime import datetime, timedelta
from .models import Product

class DateChecker:
    @staticmethod
    def get_week(date: datetime):
        weekDay = date.weekday()
        if weekDay == 6: 
            weekDay = -1
        distanceFromSunday = weekDay + 1
        distanceFromSaturday = 5 - weekDay
        weekStart = date - timedelta(days=distanceFromSunday)
        weekEnd = date + timedelta(days=distanceFromSaturday)
        return (weekStart, weekEnd)    
    
    @staticmethod
    def get_total(products):
        total = 0
        for product in products: 
            total += product.price 
        return total
    
    @staticmethod    
    def get_total_spent_in_week(week, products):
        total = 0
        for product in products: 
            if week[0] <= product.date.date() <= week[1]: 
                total += product.price
        return total
    
    @staticmethod
    def get_calendar_data(year, month):
        firstDateOfMonth = datetime(year, month, 1)
        firstDayOfMonth = firstDateOfMonth.weekday()
        if month == 12:
            firstDateOfNextMonth = datetime(year + 1, 1, 1)
        else:
            firstDateOfNextMonth = datetime(year, month + 1, 1)
        lastDateOfMonth = firstDateOfNextMonth - timedelta(days=1)
        if firstDayOfMonth == 6:
            return (range(0), range(1, lastDateOfMonth.day + 1), firstDateOfMonth)
        lastDateOfLastMonth = firstDateOfMonth - timedelta(days=1)
        distanceFromSunday = firstDayOfMonth + 1
        dateOfSunday  = firstDateOfMonth - timedelta(days=distanceFromSunday)
        return (range(dateOfSunday.day, lastDateOfLastMonth.day + 1), range(1, lastDateOfMonth.day + 1), firstDateOfMonth)
    
    @staticmethod
    def get_color_ratios(year, month, products):
        if month == 12: 
            lastDateOfMonth = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            lastDateOfMonth = datetime(year, month + 1, 1) - timedelta(days=1)
        
        ratios = {}
        for day in range(1, lastDateOfMonth.day + 1):
            total = 0
            for product in products: 
                productDate = product.date
                if (productDate.year, productDate.month, productDate.day) == (year, month, day):
                    total += product.price
            ratio = None
            if total == 0: 
                ratio = 0
            elif 0 < total <= 5:
                ratio = 5
            elif 5 < total <= 25: 
                ratio = 25
            elif 25 < total <= 50: 
                ratio = 50
            elif 50 < total <= 75: 
                ratio = 75
            else: 
                ratio = 100
            ratios[day] = ratio
        return ratios

    @staticmethod
    def get_activity_in_last_year():
        dateToday = datetime.today()
        year = dateToday.year
        month = dateToday.month
        activity = []
        products = list(Product.objects.all())
        for i in range(12):
            if month == 0: 
                month = 12
                year -= 1
            data = DateChecker.get_calendar_data(year, month)
            ratios = DateChecker.get_color_ratios(year, month, products)
            activity.append({
                'data': data, 
                'ratios': ratios
            })
            month -= 1
        return activity
        
        
        
    