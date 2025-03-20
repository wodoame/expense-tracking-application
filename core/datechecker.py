from datetime import datetime, timedelta
from .models import Product
from typing import Tuple, Union
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

def get_month(date:datetime):
    return (date.year, date.month)

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

def get_total_spent_in_month(year, month, products):
    total = 0
    for product in products:
        productDate = datefromisoformat(product.get('date')).date()
        if (productDate.year, productDate.month) == (year, month):
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

def get_activity_in_last_year(request):
    from .utils import getAllProductsFromCache # had to avoid some circular import issues
    dateToday = datetime.today()
    year = dateToday.year
    month = dateToday.month
    activity = []
    user = request.user
    products = getAllProductsFromCache(user)
    df = pd.DataFrame(products)
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'], format='ISO8601')
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


class DateRangePaginator:
    """
    A pagination class that returns date ranges based on page number.
    
    The paginator divides the period between start_date and end_date into chunks
    of a specified size, and returns the appropriate chunk for a given page number.
    
    In reverse mode, pagination starts from the end_date and moves backward.
    """
    
    def __init__(self, start_date: Union[datetime, str], end_date: Union[datetime, str], dates_per_page: int, reverse: bool = False):
        """
        Initialize the paginator with a date range and number of dates per page.
        
        Args:
            start_date: The starting date of the entire range (datetime object or string in format 'YYYY-MM-DD')
            end_date: The ending date of the entire range (datetime object or string in format 'YYYY-MM-DD')
            dates_per_page: Number of dates to include in each page range
            reverse: If True, pagination starts from end_date and moves backward
        """
        # Convert string dates to datetime objects if necessary
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
            
        # Validate inputs
        if end_date < start_date:
            raise ValueError("end_date must be greater than or equal to start_date")
        if dates_per_page <= 0:
            raise ValueError("dates_per_page must be a positive integer")
            
        self.start_date = start_date
        self.end_date = end_date
        self.dates_per_page = dates_per_page
        self.reverse = reverse
        
        # Calculate total days and number of pages
        self.total_days = (end_date - start_date).days + 1
        self.total_pages = (self.total_days + dates_per_page - 1) // dates_per_page
        
    def get_page_range(self, page_number: int) -> Tuple[datetime, datetime]:
        """
        Get the date range for a specific page number.
        
        In normal mode (reverse=False):
            Page 1 returns (start_date, start_date + dates_per_page - 1)
            Page 2 returns (start_date + dates_per_page, start_date + 2*dates_per_page - 1)
        
        In reverse mode (reverse=True):
            Page 1 returns (end_date, end_date - dates_per_page + 1)
            Page 2 returns (end_date - dates_per_page, end_date - 2*dates_per_page + 1)
        
        Args:
            page_number: The page number (1-indexed)
            
        Returns:
            In normal mode: A tuple containing (page_start_date, page_end_date)
            In reverse mode: A tuple containing (page_end_date, page_start_date)
            
        Raises:
            ValueError: If the page number is invalid
        """
        if not 1 <= page_number <= self.total_pages:
            raise ValueError(f"Invalid page number. Must be between 1 and {self.total_pages}")
        
        if not self.reverse:
            # Normal mode (start to end)
            days_offset = (page_number - 1) * self.dates_per_page
            page_start_date = self.start_date + timedelta(days=days_offset)
            page_end_date = min(
                self.start_date + timedelta(days=days_offset + self.dates_per_page - 1),
                self.end_date
            )
            return (page_start_date, page_end_date)
        else:
            # Reverse mode (end to start)
            days_offset = (page_number - 1) * self.dates_per_page
            page_end_date = self.end_date - timedelta(days=days_offset)
            page_start_date = max(
                self.end_date - timedelta(days=days_offset + self.dates_per_page - 1),
                self.start_date
            )
            return (page_end_date, page_start_date)
    
    def get_total_pages(self) -> int:
        """Return the total number of pages."""
        return self.total_pages
    

class MonthGenerator:
    def __init__(self, start_month, end_month):
        """
        Initialize the MonthGenerator with start and end months.
        
        Args:
            start_month: A tuple of (year, month) where month is 1-12
            end_month: A tuple of (year, month) where month is 1-12
        """
        # Store the limits directly since they're already in (year, month) format
        self.start = start_month
        self.end = end_month
        
        # Initialize the current position (will be properly set in __iter__)
        self.current = None
    
    def __iter__(self):
        """Return the iterator object (self)"""
        # Set current to the start position
        self.current = self.start
        return self
    
    def __next__(self):
        """Return the next month as (year, month) tuple"""
        # If current position is past the end, stop iteration
        if self.current[0] > self.end[0] or (self.current[0] == self.end[0] and self.current[1] > self.end[1]):
            raise StopIteration
        
        # Store the current position to return
        result = self.current
        
        # Advance to the next month
        year, month = self.current
        if month == 12:
            self.current = (year + 1, 1)  # Move to January of next year
        else:
            self.current = (year, month + 1)  # Move to next month of same year
            
        return result
        
    