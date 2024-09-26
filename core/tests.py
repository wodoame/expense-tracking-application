# from django.test import TestCase
from datetime import datetime, timedelta

# print(datetime.today().weekday())
weekStart = 6 # Sunday
weekEnd = 5 # Saturday

def spentThisWeek():
    dateToday = datetime.today().date()
    currentWeekDay = dateToday.weekday() 
    deltaToStart = currentWeekDay + 1 # how many days ago did the week start (Sunday starts the week)
    deltaToEnd = 5 - currentWeekDay # days left for the week to end
    weekStart = dateToday - timedelta(days=deltaToStart)
    weekEnd = dateToday + timedelta(days=deltaToEnd)
    print(currentWeekDay, weekStart, weekEnd)
    

today = datetime.today()
date = datetime(today.year, today.month, 1) # first day of current month
print(date.weekday())
lastDateOfMonth = date - timedelta(days=1) # last date of previous month
print(lastDateOfMonth)
dayOfWeek = lastDateOfMonth.weekday() # monday starts at 0
print('day of the week of last day', dayOfWeek)
if dayOfWeek == 6: 
    dayOfWeek = -1

dateOfSunday = lastDateOfMonth - timedelta(days=dayOfWeek + 1)
print(dateOfSunday)
print(range(dateOfSunday.day, lastDateOfMonth.day + 1))
# print(today.month)
# print(today.day)

for i in range(0): 
    print('hey')