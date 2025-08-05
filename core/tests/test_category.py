from django.test import TestCase, Client
from authentication.models import User
from unittest.mock import patch, MagicMock
from core.models import Category
from rest_framework import status
from core.tests.utils.category import create_random_category

ADD_CATEGORY_URL = '/implementations/categories/'
EDIT_CATEGORY_URL = '/implementations/categories/?edit=1'
DELETE_CATEGORY_URL = '/implementations/categories/?delete=1'

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

    def test_add_category(self):
        """Test adding a new category"""
        response = self.client.post(ADD_CATEGORY_URL, {
            'name': 'Test Category',
            'description': 'A category for testing'
        })
        self.assertEqual(Category.objects.count(), 1)
        self.assertTrue(Category.objects.filter(name='Test Category').exists())
        
    def test_edit_category(self):
        """Test editing an existing category"""
        category = create_random_category(self.user)
        
        response = self.client.post(EDIT_CATEGORY_URL, {
            'id': category.id,
            'name': 'Updated Category',
            'description': 'Updated description'
        })
        
        category.refresh_from_db()
        self.assertEqual(category.name, 'Updated Category')
        self.assertEqual(category.description, 'Updated description')
    
    def test_delete_category(self):
        """Test deleting a category"""
        category = create_random_category(self.user)
        self.assertEqual(Category.objects.count(), 1)
        response = self.client.post(DELETE_CATEGORY_URL, {
            'id': category.id
        })
        self.assertEqual(Category.objects.count(), 0)