from django.test import SimpleTestCase, TestCase
from rest_framework import status
from core.models import Product

class CategoryTests(TestCase):
   pass

class ProductTests(TestCase):
    def test_can_add_product(self):
        response = self.client.get('/dashboard/')
        print(response.status_code)




        
    