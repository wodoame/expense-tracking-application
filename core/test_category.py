from django.test import TestCase, Client
from django.urls import reverse
from authentication.models import User
from core.models import Category
from rest_framework import status

class CategoryCreationTest(TestCase):
    def setUp(self):
        # Create a test client
        self.client = Client()
        
        # Create a test user (if authentication is required)
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # URL for the category creation view
        self.category_create_url = '/implementations/categories/'