# from django.test import TestCase
from datetime import datetime, timedelta

today = datetime.today()

print(datetime(today.year, 12,  1) + timedelta(months=1))