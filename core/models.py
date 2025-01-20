from django.db import models
from authentication.models import User
class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True)
    name = models.CharField(max_length=25)
    description = models.TextField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products', null=True)
    name = models.CharField(max_length=25)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name
    