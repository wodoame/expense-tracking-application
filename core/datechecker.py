from datetime import datetime, timedelta
class DateChecker:
    @staticmethod
    def get_week(date):
        currentWeekDay = date.weekday() 
        deltaToStart = 0 if currentWeekDay == 6 else currentWeekDay + 1 # how many days ago did the week start (Sunday starts the week)
        deltaToEnd =  6 if currentWeekDay == 6 else  5 - currentWeekDay # days left for the week to end
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
    
    
            
        