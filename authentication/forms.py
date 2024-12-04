from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User

class UserCreationForm(UserCreationForm):
    '''the form that would be rendered for user signup'''
    class Meta:
        model = User
        fields = ['username', 'email']
        
class UserAuthenticationForm(AuthenticationForm):
    '''the form for authenticating users'''
    class Meta:
        model = User
        fields = ['username', 'email']