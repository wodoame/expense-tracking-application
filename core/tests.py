from django.test import SimpleTestCase, TestCase
from .models import Category 
from .serializers import CategorySerializer, Product
class CategoryTests(TestCase):
    def test_count_products_in_category_using_serializer(self):
        category = Category.objects.create(name='food')
        for i in range(4):
            Product.objects.create(name='beans', category=category, price=10.00, description='')
    
        categoryAsDict = CategorySerializer(category).data
        self.assertEqual(category.products.count(),
                         categoryAsDict.get('product_count'),
                         'Value produced when counting using serializer is incorrect')

        
    