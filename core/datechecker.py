from datetime import datetime, timedelta
from django.db.models import Sum, Q
from .models import Product
class DateChecker:
    @staticmethod
    def get_week(date):
        currentWeekDay = date.weekday() 
        if currentWeekDay == 6: 
            currentWeekDay = -1
        deltaToStart = currentWeekDay + 1 # how many days ago did the week start (Sunday starts the week)
        deltaToEnd =  5 - currentWeekDay # days left for the week to end
        weekStart = date - timedelta(days=deltaToStart)
        weekEnd = date + timedelta(days=deltaToEnd)
        return weekStart, weekEnd
    
    @staticmethod
    def spent_in_week(week, items):
        weekStart, weekEnd = week
        totalCost = 0
        for item in items:
            if weekStart <= item.date.date() <= weekEnd: 
                totalCost += item.price 
        return totalCost 
    
    @staticmethod
    def get_date_today():
        return datetime.today().date() 
    
    @staticmethod
    def get_date_yesterday():
        return DateChecker.get_date_today() - timedelta(days=1)
    
    # helps create the calendar structure
    @staticmethod
    def get_calendar_data(year, month):
        firstDateOfMonth = datetime(year, month, 1) # first day of current month
        firstDateOfNextMonth = None
        if month == 12: 
            firstDateOfNextMonth = datetime(year + 1, 1, 1)
        else: 
            firstDateOfNextMonth = datetime(year, month + 1, 1)
        lastDateOfCurrentMonth = firstDateOfNextMonth - timedelta(days=1)
        # if the first day is a Sunday then the calendar starts from the beginning 
        if firstDateOfMonth.weekday() == 6:
            return (range(0), range(1, lastDateOfCurrentMonth.day + 1), firstDateOfMonth)
        lastDateOfPrevMonth = firstDateOfMonth - timedelta(days=1)
        dayOfWeek = lastDateOfPrevMonth.weekday() # day of the week of the last day
        if dayOfWeek == 6: 
            dayOfWeek = -1 # for the calculations Sunday is considered as -1, Monday=0, Tuesday=1, ... and so on
        distanceFromSunday = dayOfWeek + 1
        dayOfSunday = lastDateOfPrevMonth.day - distanceFromSunday
        return (range(dayOfSunday, lastDateOfPrevMonth.day + 1), range(1, lastDateOfCurrentMonth.day + 1), firstDateOfMonth)
    
    @staticmethod
    def get_color_ratios(year, month, products):
        firstDateOfNextMonth = None
        # if we are in December than we set the first day of next month to January of the next year
        if month == 12:
            firstDateOfNextMonth = datetime(year + 1, 1, 1)
        else: 
            firstDateOfNextMonth = datetime(year, month + 1, 1)
        lastDateOfMonth = firstDateOfNextMonth - timedelta(days=1)
        lastDayOfMonth = lastDateOfMonth.day
        ratios = {}
        # loop over every day in the month
        for day in range(1, lastDayOfMonth + 1): 
            total = 0
            for product in products: 
                if (product.date.year, product.date.month, product.date.day) == (year, month, day):
                    total += product.price
                    # for better efficiency products which have already used for calculations should be removed somehow
                    
            ratio = None
            if total == 0: 
                ratio = 0
            elif 0 < total < 25:
                ratio = 5
            elif 25 <= total < 50: 
                ratio = 25
            elif 50 <= total < 75: 
                ratio = 50
            elif 75 <= total < 100: 
                ratio = 75
            else: 
                ratio = 100
            ratios[day] = ratio # denominator could be the highest daily spending for the month
        return ratios 
    
    @staticmethod
    def get_activity_in_last_year():
        activity = []
        today = datetime.today()
        month = today.month 
        year = today.year
        products = list(Product.objects.filter(Q(date__year=year)| Q(date__year=year - 1)))
        for i in range(12):
            # check if we've gone to the previous year
            if month == 0:
                month = 12 
                year -= 1
            data = DateChecker.get_calendar_data(year, month)
            ratios = DateChecker.get_color_ratios(year, month, products)
            activity.append(
                {
                    'lastDays': data[0],
                    'ratios': ratios, 
                    'date': data[2] 
                }
            )
            month -= 1
        return activity
        
    
            
        