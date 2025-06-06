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

        totalSpentThisMonth = user.monthly_spendings.filter(month_start=self.thisMonth[0]).first()
        totalSpentLastMonth = user.monthly_spendings.filter(month_start=self.lastMonth[0]).first()
        highestMonthlySpending = user.monthly_spendings.first()
        if totalSpentThisMonth:
            totalSpentThisMonth = totalSpentThisMonth.total_amount
        if totalSpentLastMonth:
            totalSpentLastMonth = totalSpentLastMonth.total_amount
        if highestMonthlySpending:
            highestMonthlySpending = highestMonthlySpending.total_amount

        return [
            {'text': 'Total spent this month', 'data': totalSpentThisMonth or 0},
            {'text': 'Total spent last month', 'data': totalSpentLastMonth or 0},
            {'text': 'Highest monthly spending', 'data': highestMonthlySpending or 0}
        ]
        
        
class Context:
    def __init__(self, strategy):
        self.strategy = strategy 
        
    def apply(self):
        return self.strategy.calculate()