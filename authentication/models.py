from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    '''the user model'''
    
    
    def __str__(self):
        return self.username
    