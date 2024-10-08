from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.FloatField()
    description = models.TextField(max_length=128, null=True, blank=True) 
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name 