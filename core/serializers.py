from rest_framework import serializers
from .models import Product, Category
import pandas as pd
class CategorySerializer(serializers.ModelSerializer):
    class Meta: 
        model = Category
        fields = ['id', 'name', 'description']
        
class CategorySerializerWithMetrics(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    class Meta: 
        model = Category
        fields = ['id', 'name', 'description', 'metrics']
        
    def get_metrics(self, obj):
        products = ProductPriceSerializer(obj.products.all(), many=True).data
        df = pd.DataFrame(products)
        metrics = {
            "product_count": 0, 
            "total_amount_spent": 0
        }
        if not df.empty:
            # NOTE: explicitly convert to the respective data types since the original result from pandas is an object
            metrics['product_count'] = int(df.get('name').count())
            metrics['total_amount_spent'] = float(df.get('price').sum())
        return metrics    
    
class ProductSerializer(serializers.ModelSerializer): 
    category = CategorySerializer() 
    name = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    class Meta: 
        model = Product
        fields = '__all__'
    
    def get_name(self, product):
        return product.get_name()
    
    def get_description(self, product):
        return product.get_description()

class ProductPriceSerializer(serializers.ModelSerializer):
    class Meta: 
        model = Product
        fields = ['name', 'price']
