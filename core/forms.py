from django import forms 
from .models import Product

class AddProductForm(forms.ModelForm):
    class Meta: 
        model = Product
        fields = '__all__'
        exclude = ['price', 'user']