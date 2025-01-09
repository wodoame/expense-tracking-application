from django.test import SimpleTestCase, TestCase
from django.test import Client
from unittest.mock import patch
from rest_framework import status
from core.models import Product
from authentication.models import User
from django.shortcuts import redirect

class CategoryTests(SimpleTestCase):
   pass

class ProductTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

    def test_can_add_product(self):
        product = Product.objects.create(name='bread', price=12.00)
        self.assertEqual(Product.objects.count(), 1)

    @patch('core.views.redirect')
    def test_can_add_product_without_category_via_POST(self, mocked_redirect):
        self.url = '/implementations/dashboard/'
        mocked_redirect.return_value = redirect(self.url)
        client = Client()
        loginData = {
            'username':'testuser',
            'password': 'testpass'
        }
        client.login(**loginData)
        data = {
            'name': 'bread',
            'cedis': '10',
            'pesewas': '50',
            'category': '',
            'description': ''
        }
        response = client.post(self.url, data)
        self.assertFalse(response.status_code == status.HTTP_404_NOT_FOUND, 'The URL specified is incorrect')
        self.assertEqual(Product.objects.count(), 1, 'Product could not be added')


    @patch('core.views.redirect')
    def test_can_add_product_with_category_via_POST(self, mocked_redirect):
        self.url = '/implementations/dashboard/'
        mocked_redirect.return_value = redirect(self.url)
        client = Client()
        loginData = {
            'username':'testuser',
            'password': 'testpass'
        }
        client.login(**loginData)
        data = {
            'name': 'bread',
            'cedis': '10',
            'pesewas': '50',
            'category': '0',
            'newCategoryName': 'Food',
            'description': ''
        }
        response = client.post(self.url, data)
        self.assertFalse(response.status_code == status.HTTP_404_NOT_FOUND, 'The URL specified is incorrect')
        self.assertEqual(Product.objects.count(), 1, 'Product could not be added')






        
    