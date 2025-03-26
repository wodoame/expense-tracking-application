from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Product, Category # Adjust the import path to match your project structure
from authentication.models import User

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
    
    def test_create_product_with_bad_category_name(self):
        """
        Test creating a product with a category name that contains invalid characters.
        """
        category = Category.objects.create(name='Repairs & Electricals') # & is the bad character
        
        data = {
            'name': 'Test Product',  # Contains invalid characters
            'date': '2025-03-26',
            'description': 'A detailed description of the test product', 
            'category': category.id
        }
        
        # Send POST request
        response = self.client.post(self.category_create_url, data)
        # TODO: complete the test