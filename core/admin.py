from django.contrib import admin
from .models import *

admin.site.register(Product)
admin.site.register(Category)
admin.site.register(Settings)
admin.site.register(KeyValuePair)
admin.site.register(WeeklySpending)