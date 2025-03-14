from django import forms 
from .models import *

class AddProductForm(forms.ModelForm):
    class Meta: 
        model = Product
        fields = '__all__'
        exclude = ['price', 'user', 'date']
        
class AddCategoryForm(forms.ModelForm):
    class Meta: 
        model = Category
        fields = '__all__'
        exclude = ['user']