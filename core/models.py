from django.db import models
from authentication.models import User
from .encryption import EncryptionHelper
from django.conf import settings 
from django.utils import timezone

class Category(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories', null=True)
    name = models.CharField(max_length=25)
    description = models.TextField(max_length=255, blank=True, null=True)
    
    class Meta:
        unique_together = ['user', 'name']
        # Alternative in newer Django versions:
        # constraints = [
        #     models.UniqueConstraint(fields=['user', 'name'], name='unique_user_category')
        # ]
    
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
        return self.name
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
    search = models.JSONField(default=dict)
    
    def __str__(self):
        return self.user.username + ' settings'
    
class KeyValuePair(models.Model):
    key = models.TextField(unique=True)
    value = models.TextField()
    
    def __str__(self):
        return self.key
    
    