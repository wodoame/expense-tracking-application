from datetime import datetime, timedelta
from .models import Product
from .serializers import ProductSerializer
import pandas as pd

def get_week(date: datetime):
    weekDay = date.weekday()
    if weekDay == 6: 
        weekDay = -1
    distanceFromSunday = weekDay + 1
    distanceFromSaturday = 5 - weekDay
    weekStart = date - timedelta(days=distanceFromSunday)
    weekEnd = date + timedelta(days=distanceFromSaturday)
    return (weekStart, weekEnd)    

def datefromisoformat(date: str):
    return datetime.fromisoformat(date)
    
def get_total(products):
    total = 0
    for product in products: 
        total += product.get('price')
    return total

def collectDates(products: list[dict]):
    uniqueDates = list(set(datefromisoformat(product.get('date')).date() for product in products))
    return uniqueDates
        

def get_total_spent_in_week(week, products):
    total = 0
    for product in products: 
        if week[0] <= datefromisoformat(product.get('date')).date() <= week[1]: 
            total += product.get('price')
    return total

def get_calendar_data(year, month):
    firstDateOfMonth = datetime(year, month, 1)
    firstDayOfMonth = firstDateOfMonth.weekday()
    if month == 12:
        firstDateOfNextMonth = datetime(year + 1, 1, 1)
    else:
        firstDateOfNextMonth = datetime(year, month + 1, 1)
    lastDateOfMonth = firstDateOfNextMonth - timedelta(days=1)
    if firstDayOfMonth == 6:
        return (range(0), range(1, lastDateOfMonth.day + 1), firstDateOfMonth)
    lastDateOfLastMonth = firstDateOfMonth - timedelta(days=1)
    distanceFromSunday = firstDayOfMonth + 1
    dateOfSunday  = firstDateOfMonth - timedelta(days=distanceFromSunday)
    return (range(dateOfSunday.day, lastDateOfLastMonth.day + 1), range(1, lastDateOfMonth.day + 1), firstDateOfMonth)

def get_color_ratios(year, month, df: pd.DataFrame):
    if month == 12: 
        lastDateOfMonth = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        lastDateOfMonth = datetime(year, month + 1, 1) - timedelta(days=1)
    
    ratios = {}
    totals = []
    maxDailySpendingThisMonth = 0
    
    # determine some metrics like highest spent in the month
    for day in range(1, lastDateOfMonth.day + 1):
        total = 0 # total for the day
        if not df.empty:
            date = datetime(year, month, day).date() # current date
            filteredDf = df[df.get('date').dt.date == date] # create a dataframe which contains products bought on a specific day
            total = filteredDf.get('price').sum() # find the sum
        totals.append([day, total])
        maxDailySpendingThisMonth = max(maxDailySpendingThisMonth, total)
    
    
    # calculate color ratio based on highest daily spending
    for day, total in totals:
        ratio = None
        conversion = None # percentage of highest daily spending
        if maxDailySpendingThisMonth != 0:
            conversion = (total / maxDailySpendingThisMonth) * 100
        else: 
            conversion = 0
            
        if conversion == 0: 
            ratio = 0
        elif 0 < conversion <= 5:
            ratio = 5
        elif 5 < conversion <= 25: 
            ratio = 25
        elif 25 < conversion<= 50: 
            ratio = 50
        elif 50 < conversion <= 75: 
            ratio = 75
        else: 
            ratio = 100
        ratios[day] = ratio
    return ratios

def get_activity_in_last_year():
    dateToday = datetime.today()
    year = dateToday.year
    month = dateToday.month
    activity = []
    products = ProductSerializer(Product.objects.all(), many=True).data
    df = pd.DataFrame(products)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    for i in range(12):
        if month == 0: 
            month = 12
            year -= 1
        data = get_calendar_data(year, month)
        ratios = get_color_ratios(year, month, df)
        activity.append({
            'data': data, 
            'ratios': ratios
        })
        month -= 1
    return activity
        
        
        
    