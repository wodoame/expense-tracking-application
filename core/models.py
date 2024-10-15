from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=128)
    price = models.FloatField()
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(max_length=255, blank=True)
    
    def __str__(self):
        return self.name