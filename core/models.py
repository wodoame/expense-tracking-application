from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name
    
class Product(models.Model):
    name = models.CharField(max_length=128)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True)
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name
    