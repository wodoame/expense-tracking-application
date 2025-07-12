from django.test import TestCase, Client
from authentication.models import User
from unittest.mock import patch, MagicMock

class CategoryTestCase(TestCase):
    """Base test case with common setup for category tests"""

    def setUp(self):
        """Set up test data and authenticated user"""
        self.client = Client()
        
        # Create test user
        self.username = 'testuser'
        self.password = 'testpass123'
        self.email = 'test@example.com'
        
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        
        # Authenticate user
        self.client.login(username=self.username, password=self.password)
        
        # Create mock request object
        self.mock_request = MagicMock()
        self.mock_request.user = self.user
    
    def tearDown(self):
        """Clean up after tests"""
        self.client.logout()