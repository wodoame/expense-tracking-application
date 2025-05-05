from datetime import datetime, timedelta
import core.datechecker as dc 
from core.models import User, WeeklySpending
from .utils import getSettings

class WeeklyStats:
    def __init__(self, user: User):
        self.user = user
        self.thisWeek = dc.get_week_monday_based(datetime.today().date())
        self.lastWeek = dc.get_week_monday_based(datetime.today().date() - timedelta(days=7))

        
    def calculate(self):
        user = self.user
        settings = getSettings(user)
        if not settings.populated_weekly_spending:
            WeeklySpending.populate_weekly_spending(user)
            
        totalSpentThisWeek = user.weekly_spendings.filter(week_start=self.thisWeek[0]).first()
        totalSpentLastWeek = user.weekly_spendings.filter(week_start=self.lastWeek[0]).first()
        highestWeeklySpending = user.weekly_spendings.first()
        if totalSpentThisWeek:
            totalSpentThisWeek = totalSpentThisWeek.total_amount
        if totalSpentLastWeek:
            totalSpentLastWeek = totalSpentLastWeek.total_amount
        if highestWeeklySpending:   
            highestWeeklySpending = highestWeeklySpending.total_amount
        
        return [{'text': 'Total spent this week', 'data':totalSpentThisWeek or 0},
                {'text': 'Total spent last week', 'data':totalSpentLastWeek or 0},
                {'text': 'Highest weekly spending', 'data':highestWeeklySpending or 0}
                ]

class MonthlyStats:
    def __init__(self, products: list[dict], user: User):
        self.products = products 
        self.user = user
        self.generator = dc.MonthGenerator(dc.get_month(user.date_joined), dc.get_month(datetime.today()))
        self.monthsData = {} 
        # preprocessing: initialize all months data
        for month in self.generator:
            key = str(month)
            self.monthsData[key] = {'total': 0}    
    
    def calculate(self):
        # initialize some metrics
        totalSpentThisMonth = 0
        totalSpentLastMonth = 0
        highestMonthlySpending = 0
        for product in self.products:
            date = dc.datefromisoformat(product.get('date')).date()
            month = dc.get_month(date)
            key = str(month)
            self.monthsData[key]['total'] += product.get('price')
            highestMonthlySpending = max(highestMonthlySpending, self.monthsData[key]['total'])
    
        dateToday = datetime.today()
        thisMonth = dc.get_month(dateToday)
        lastMonth = dc.get_month(datetime(dateToday.year, dateToday.month, 1) - timedelta(days=1)) 
        totalSpentThisMonth = self.monthsData[str(thisMonth)]['total']
        if len(self.monthsData) > 1: 
            totalSpentLastMonth = self.monthsData[str(lastMonth)]['total']
        return [{'text': 'Total spent this month', 'data':totalSpentThisMonth},
                {'text': 'Total spent last month', 'data':totalSpentLastMonth},
                {'text': 'Highest monthly spending', 'data':highestMonthlySpending}
              ]
  
        
        
        
class Context:
    def __init__(self, strategy):
        self.strategy = strategy 
        
    def apply(self):
        return self.strategy.calculate()