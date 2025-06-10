from datetime import datetime, timedelta
import core.datechecker as dc 
from core.models import User, WeeklySpending, MonthlySpending
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
            
        thisWeekData = user.weekly_spendings.filter(week_start=self.thisWeek[0]).first()
        lastWeekData = user.weekly_spendings.filter(week_start=self.lastWeek[0]).first()
        highestWeekData = user.weekly_spendings.first()

        return [
               self.get_stat(thisWeekData, 'Total spent this week'),
               self.get_stat(lastWeekData, 'Total spent last week'),
               self.get_stat(highestWeekData, 'Highest weekly spending')
            ]
    def get_stat(self, data: WeeklySpending, label:str):
        UNSET_ID = -1
        result = {'text': label, 'data': 0, 'id': UNSET_ID}
        if data:
             result['id'] = data.id
             result['data'] = data.total_amount
        return result

class MonthlyStats:
    def __init__(self, user: User):
        self.user = user
        self.thisMonth = dc.get_month(datetime.today().date())
        last_month_date = self.thisMonth[0] - timedelta(days=1)
        self.lastMonth = dc.get_month(last_month_date)

    def calculate(self):
        user = self.user
        # If you have a populated_monthly_spending flag, check and populate here
        settings = getSettings(user)
        if not settings.populated_monthly_spending:
            MonthlySpending.populate_monthly_spending(user)

        thisMonthData = user.monthly_spendings.filter(month_start=self.thisMonth[0]).first()
        lastMonthData = user.monthly_spendings.filter(month_start=self.lastMonth[0]).first()
        highestMonthData = user.monthly_spendings.first()
       
        return [
               self.get_stat(thisMonthData, 'Total spent this month'),
               self.get_stat(lastMonthData, 'Total spent last month'),
               self.get_stat(highestMonthData, 'Highest monthly spending')
        ]
        
    def get_stat(self, data: MonthlySpending, label:str):
        UNSET_ID = -1
        result = {'text': label, 'data': 0, 'id': UNSET_ID}
        if data:
             result['id'] = data.id
             result['data'] = data.total_amount
        return result
        
        
class Context:
    def __init__(self, strategy):
        self.strategy = strategy 
        
    def apply(self):
        return self.strategy.calculate()