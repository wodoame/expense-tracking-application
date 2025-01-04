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
            
        return [totalSpentThisWeek, totalSpentLastWeek, highestWeeklySpending]
        
class Context:
    def __init__(self, strategy):
        self.strategy = strategy 
        
    def apply(self):
        return self.strategy.calculate()