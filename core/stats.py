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