from django.db import models
from django.db.models import Sum
from django.db.models.functions import TruncWeek
from authentication.models import User
from .encryption import EncryptionHelper
from django.conf import settings 
from django.utils import timezone
from datetime import timedelta, datetime
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True)
    name = models.CharField(max_length=25)
    description = models.TextField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)
    name = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    price = models.FloatField()
    date = models.DateTimeField(default=timezone.now, blank=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.encryption_helper.decrypt(self.name)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.encryption_helper = EncryptionHelper(key=settings.ENCRYPTION_KEY)

    def save(self, *args, **kwargs):
        # Encrypt sensitive fields before saving
        if not self.encryption_helper.is_encrypted(self.name):
            self.name = self.encryption_helper.encrypt(self.name)
        if not self.encryption_helper.is_encrypted(self.description): 
            self.description = self.encryption_helper.encrypt(self.description)
        super().save(*args, **kwargs)

    def get_name(self):
        # Decrypt the item name when needed
        return self.encryption_helper.decrypt(self.name)

    def get_description(self):
        # Decrypt the description when needed
        return self.encryption_helper.decrypt(self.description)
    
class Settings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')
    populated_weekly_spending = models.BooleanField(default=False) 
    
    def __str__(self):
        return self.user.username + ' settings'
    
class KeyValuePair(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    
    def __str__(self):
        return self.key

class WeeklySpending(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='weekly_spendings', null=True)
    week_start = models.DateField()
    week_end = models.DateField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    
    @staticmethod
    def populate_weekly_spending(user: User):
        # Group by week and calculate total amount
        weekly_totals = (user.products
                         .annotate(
                           week_start=TruncWeek('date')) # week starts on Sunday so minus 1 day
                         .values('week_start')
                         .annotate(total_amount=Sum('price'))
                         )
        
        # Insert or update WeeklySpending records
        for entry in weekly_totals:
            WeeklySpending.objects.update_or_create(
                user=user,
                week_start=entry['week_start'],
                week_end=entry['week_start'] + timedelta(days=6),
                defaults={'total_amount': entry['total_amount']}
            )
            
        user.settings.populated_weekly_spending = True
        user.settings.save() 
        
    @staticmethod
    def update_weekly_spending(user: User, date: datetime):
        from .datechecker import get_week_monday_based
        week = get_week_monday_based(date)
        weekly_stats = (user.products
            .filter(date__date__range=(week[0], week[1]))
            .annotate(week_start=TruncWeek('date'))
            .values('week_start')
            .annotate(total_amount=models.Sum('price'))
            )
        
        # get or create the WeeklySpending record for the week
        weeklySpending, created = WeeklySpending.objects.get_or_create(user=user, week_start=week[0], week_end=week[1])
        if weekly_stats.count() > 0:
            weeklySpending.total_amount = weekly_stats[0]['total_amount']
            weeklySpending.save()
        else: # if there are no products in that week, set total_amount to 0
            weeklySpending.total_amount = 0
            weeklySpending.save()

        
    class Meta:
        ordering = ['-total_amount']
        
    def __str__(self):
        return self.user.username + ' weekly spending from ' + str(self.week_start) + ' to ' + str(self.week_end) + ': ' + str(self.total_amount)
    
    