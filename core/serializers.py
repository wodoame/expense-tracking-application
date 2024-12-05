from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    class Meta: 
        model = Category
        fields = ['id', 'name', 'product_count']
        
    def get_product_count(self, obj):
        return obj.products.count()
    
class ProductSerializer(serializers.ModelSerializer): 
    category = CategorySerializer() 
    class Meta: 
        model = Product
        fields = '__all__'
