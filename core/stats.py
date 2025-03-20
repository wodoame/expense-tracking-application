from datetime import datetime, timedelta
import core.datechecker as dc 
from core.models import User

class WeeklyStats:
    def __init__(self, products: list[dict], user: User):
        self.products = products
        self.user = user
        self.firstWeek = dc.get_week(user.date_joined.date())
        self.thisWeek = dc.get_week(datetime.today().date())
        self.paginator = dc.DateRangePaginator(self.firstWeek[0], self.thisWeek[1], 7)
        self.numberOfWeeks = self.paginator.get_total_pages()
        
        # preprocessing stage: intialize all week data
        self.weeksData = {}
        for pageNumber in range(1, self.numberOfWeeks + 1):
            dateRange = self.paginator.get_page_range(pageNumber)
            key = self.make_key(dateRange)
            self.weeksData[key] = {'total': 0} # add any metric that needs to be calculated for each week
        print(self.weeksData)
        
    def calculate(self):
        # intialize some key metrics
        highestWeeklySpending = 0
        totalSpentThisWeek = 0
        totalSpentLastWeek = 0
        thisWeek = self.thisWeek
        lastWeek = (self.thisWeek[0] - timedelta(weeks=1), self.thisWeek[1] - timedelta(weeks=1))
        
        # perform the calculations
        for product in self.products:
            date = dc.datefromisoformat(product.get('date')).date()
            week = dc.get_week(date)
            key = self.make_key(week)
            self.weeksData[key]['total'] += product.get('price')
            highestWeeklySpending = max(highestWeeklySpending, self.weeksData[key]['total'])
        
        totalSpentThisWeek = self.weeksData[self.make_key(thisWeek)]['total']
        totalSpentLastWeek = self.weeksData[self.make_key(lastWeek)]['total']
        return [{'text': 'Total spent this week', 'data':totalSpentThisWeek},
                {'text': 'Total spent last week', 'data':totalSpentLastWeek},
                {'text': 'Highest weekly spending', 'data':highestWeeklySpending}
                ]
        
    def make_key(self, week):
        return str((
            week[0].strftime('%Y-%m-%d'),
            week[1].strftime('%Y-%m-%d')
        ))

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