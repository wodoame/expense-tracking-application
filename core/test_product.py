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
        self.edit_url = '/implementations/dashboard/?delete=1'
    
    def test_create_product_no_category(self):
        """
        Test creating a product with valid data.
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
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.add_url, data)
        
        # Check if the response is a redirect
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        
        # Check if the product has been created
        self.assertEqual(Product.objects.count(), 1)
        
        # Check if the product's details match the provided data
        product = Product.objects.get(name='Test Product')
        self.assertTrue(product.name == 'Test Product')