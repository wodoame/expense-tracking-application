from datetime import datetime, timedelta
from django.db.models import Sum
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
    
    @staticmethod
    def get_calendar_data(month):
        today = datetime.today()
        date = datetime(today.year, month, 1) # first day of current month
        lastDateOfCurrentMonth = datetime(today.year, month + 1, 1) - timedelta(days=1)
        if date.weekday() == 6:
            return (range(0), range(1, lastDateOfCurrentMonth.day + 1), date)
        lastDateOfPrevMonth = date - timedelta(days=1)
        dayOfWeek = lastDateOfPrevMonth.weekday() # day of the week of the last day
        if dayOfWeek == 6: 
            dayOfWeek = -1 
        distanceFromSunday = dayOfWeek + 1
        dayOfSunday = lastDateOfPrevMonth.day - distanceFromSunday
        return (range(dayOfSunday, lastDateOfPrevMonth.day + 1), range(date.day, lastDateOfCurrentMonth.day + 1), date)
    
    @staticmethod
    def get_color_ratios(month, products):
        today = datetime.today()
        lastDateOfMonth = datetime(today.year, month + 1, 1) - timedelta(days=1)
        lastDayOfMonth = lastDateOfMonth.day
        ratios = {}
        for day in range(1, lastDayOfMonth + 1): 
            total = products.filter(date__day=day).aggregate(total=Sum('price', default=0)).get('total')
            ratio = 0
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
    def activity():
        pass 
        
    
            
        