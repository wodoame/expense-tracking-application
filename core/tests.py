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

spentThisWeek()