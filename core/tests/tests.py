from django.test import TestCase, Client
from core.serializers import ProductSerializer
from core.models import Product, User
from core.utils import groupByDate
from django.test import Client
from core.tests.utils.product import create_random_products

class Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client = Client()
        # self.client.login(username='testuser', password='testpass123')
        
    def test_group_products_by_date(self):
        create_random_products(self.user, count=10)
        products = ProductSerializer(
            Product.objects.all(), 
            many=True
        ).data # serializer products
        records = groupByDate(products)
        # a record is a day with a list of products bought on that day 
        # ( For example {'date': '2025-06-09',
        # 'products': [{'id': 6, 'category': None, 'name': 'Butter', 'description': 'Gluten free.', 'price': 2.97, 'date': '2025-06-09T19:18:27.769728Z', 'user': 1, 'date_for_grouping': '2025-06-09'}], 'total': 2.97})
        number_of_products_grouped = 0
        for record in records:
            number_of_products_grouped += len(record['products'])
            
        # check if the number of products in the grouped records is equal to the total number of products passed to the function
        self.assertEqual(len(products), number_of_products_grouped)