from django.test import TestCase, Client
from .models import Product
from authentication.models import User
from rest_framework import status 
from datetime import datetime

class ProductCreationTestCase(TestCase):
    def setUp(self):
        """
        Set up any necessary data or configurations before running tests.
        This method is called before each test method.
        """
        # Create a test client
        self.client = Client()
        
        # Create a test user (if authentication is required)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.add_url = '/implementations/dashboard/'
        self.edit_url = '/implementations/dashboard/?edit=1'
        self.delete_url = '/implementations/dashboard/?delete=1'
    
    def test_add_product(self):
        """
        required data:
        - name: str
        - cedis: int
        - pesewas: int
        - description: str
        - date: str (YYYY-MM-DD)
        
        optional data: 
        - category: str (number)
        - newCategoryName: str (if category is 0 meaning a new category is to be created)
        """
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data
        data = {
            'name': 'Test Product',
            'cedis': 10,
            'pesewas': 50,
            'description': 'This is a test product.',
            'date': datetime.today().strftime('%Y-%m-%d'),
            'category': 0, 
            'newCategoryName': 'Test Category'
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.add_url, data)
        
        # Check if the response is a redirect
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK)
        product = Product.objects.latest('date')
        
        # Check if the product has been created
        self.assertEqual(Product.objects.count(), 1)
    
    
    def test_edit_product(self):
        """
        required data:
        - name: str
        - cedis: int
        - pesewas: int
        - description: str
        - date: str (YYYY-MM-DD)
        - new-date: str (YYYY-MM-DD)
        
        optional data: 
        - category: str (number)
        - newCategoryName: str (if category is 0 meaning a new category is to be created)
        """
        product = Product.objects.create(
            user=self.user,
            name='Test Product',
            price=10.50,
            description='This is a test product.',
            date=datetime.today().strftime('%Y-%m-%d'),
            category=None
        )
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Change the name of the product
        data = {
            'id': product.id, 
            'name': 'Test Product Edited',
            'cedis': 10,
            'pesewas': 50,
            'description': 'This is a test product.',
            'date': datetime.today().strftime('%Y-%m-%d'),
            'new-date': datetime.today().strftime('%Y-%m-%d'),
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.edit_url, data)
        
        # Check if the response is a redirect
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK)
        product = Product.objects.get(id=product.id)
        self.assertEqual(product.get_name(), 'Test Product Edited') 
        
    
    
    def test_delete_product(self):
        product = Product.objects.create(
            user=self.user,
            name='Test Product',
            price=10.50,
            description='This is a test product.',
            date=datetime.today().strftime('%Y-%m-%d'),
            category=None
        )
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Change the name of the product
        data = {
            'id': product.id, 
            'date': datetime.today().strftime('%Y-%m-%d'),
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.delete_url, data)
        
        # Check if the response is a redirect
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK)
        self.assertRaises(Product.DoesNotExist, Product.objects.get, id=product.id)
        