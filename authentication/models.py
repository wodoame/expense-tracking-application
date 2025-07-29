from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    '''the user model'''
    email = models.EmailField(unique=True)
    profile_picture = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.username
    