from rest_framework import serializers
from .models import *
import pandas as pd
from core.templatetags.custom_filters import dateOnly
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

class CategorySerializerWithFilter(serializers.ModelSerializer):
    metrics = serializers.SerializerMethodField()
    class Meta: 
        model = Category
        fields = ['id', 'name', 'description', 'metrics']
        
    def get_metrics(self, obj):
        date_filter = self.context.get('date_filter')
        products = ProductPriceSerializer(obj.products.filter(date__date__range=date_filter), many=True).data
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
        
class WeeklySpendingSerializer(serializers.ModelSerializer):
    week_start = serializers.SerializerMethodField()
    week_end = serializers.SerializerMethodField()
    class Meta:
        model = WeeklySpending
        fields = ['id', 'total_amount', 'week_start', 'week_end', 'custom_name']

    def get_week_start(self, obj):
        return dateOnly(obj.week_start)

    def get_week_end(self, obj):
        return dateOnly(obj.week_end)

class MonthlySpendingSerializer(serializers.ModelSerializer):
    month_start = serializers.SerializerMethodField()
    month_end = serializers.SerializerMethodField()
    class Meta:
        model = MonthlySpending
        fields = ['id', 'total_amount', 'month_start', 'month_end']

    def get_month_start(self, obj):
        return dateOnly(obj.month_start)

    def get_month_end(self, obj):
        return dateOnly(obj.month_end)
