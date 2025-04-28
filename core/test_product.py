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
    
    def test_add_product(self):
        """
        required data:
        - name: str
        - cedis: int
        - pesewas: int
        - description: str
        - date: str (YYYY-MM-DD)
        
        optional data: 
        - category: str
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
            'category': 'Test Category'
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.add_url, data)
        
        # Check if the response is a redirect
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK)
        product = Product.objects.latest('date')
        
        # Check if the product has been created
        self.assertEqual(Product.objects.count(), 1)
        