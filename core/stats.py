from datetime import datetime, timedelta
import core.datechecker as dc 

class WeeklyStats:
    def __init__(self, products, user):
        self.products = products
        self.user = user
        
    def calculate(self):
        dateToday = datetime.today().date()
        thisWeek = dc.get_week(dateToday)
        lastWeek = (thisWeek[0] - timedelta(days=7), thisWeek[1] - timedelta(days=7))
        totalSpentThisWeek = dc.get_total_spent_in_week(thisWeek, self.products)
        totalSpentLastWeek = dc.get_total_spent_in_week(lastWeek, self.products)
        highestWeeklySpending = max(totalSpentThisWeek, totalSpentLastWeek)
        week = lastWeek

        while week[0] >= self.user.date_joined.date(): 
            week = (week[0] - timedelta(days=7), week[1] - timedelta(days=7))
            totalSpent = dc.get_total_spent_in_week(week, self.products)
            highestWeeklySpending = max(highestWeeklySpending, totalSpent)
            
        return [{'text': 'Total spent this week', 'data':totalSpentThisWeek},
                {'text': 'Total spent last week', 'data':totalSpentLastWeek},
                {'text': 'Highest weekly spending', 'data':highestWeeklySpending}
                ]

class MonthlyStats:
    def __init__(self, products, user):
        self.products = products 
        self.user = user
    
    def calculate(self):
        dateToday = datetime.today().date()
        year = dateToday.year
        month = dateToday.month
        totalSpentThisMonth = dc.get_total_spent_in_month(year, month, self.products)
        # set month to 12 if current month is January
        if month == 1:
            year -= 1
            month = 12
        else: 
            month -= 1 
        totalSpentLastMonth = dc.get_total_spent_in_month(year, month, self.products)
        highestMonthlySpending = max(totalSpentThisMonth, totalSpentLastMonth)
        date = datetime(year, month, 1)
        dateJoined = self.user.date_joined
        endDate = None # I'm setting the end date to the month before the user joined so that we can still find items bought in the month they joined
        if dateJoined.month == 1: 
            endDate = datetime(dateJoined.year -1, 12, 1)
        else: 
            endDate = datetime(dateJoined.year, dateJoined.month -1, 1)

        while date.date() > endDate.date():
            if date.month == 1: 
                date = datetime(date.year - 1, 12, 1)
            else:
                date = datetime(date.year, date.month -1, 1)
            totalSpent = dc.get_total_spent_in_month(date.year, date.month, self.products)
            highestMonthlySpending = max(totalSpent, highestMonthlySpending)
        return [{'text': 'Total spent this month', 'data':totalSpentThisMonth},
                {'text': 'Total spent last month', 'data':totalSpentLastMonth},
                {'text': 'Highest monthly spending', 'data':highestMonthlySpending}
              ]
  
        
        
        
class Context:
    def __init__(self, strategy):
        self.strategy = strategy 
        
    def apply(self):
        return self.strategy.calculate()