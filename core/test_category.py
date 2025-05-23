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
        self.create_category_url = '/implementations/categories/'
        self.edit_category_url = '/implementations/categories/?edit=1'
        self.delete_category_url = '/implementations/categories/?delete=1'
        
    def test_create_category(self):
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data for category creation 
        data = {
            'name': 'Test Category',
            'description': 'This is a test category.',
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.create_category_url, data)
        
        # Check if the response is a redirect
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK)
        self.assertEqual(Category.objects.count(), 1) 
    
    def test_edit_category(self):
        # Create a category to edit
        category = Category.objects.create(
            name='Name 1',
            description='This is an old category.'
        )
        
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data for category editing
        data = {
            'id': category.id,
            'name': 'Name 2',
            'description': 'This is an updated category.',
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.edit_category_url, data)
        
        # Check if the response is a redirect or success
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK, f'status code: {response.status_code}')
        category.refresh_from_db()
        self.assertEqual(category.name, 'Name 2')
        self.assertEqual(category.description, 'This is an updated category.')
        
    def test_delete_category(self):
        # Create a category to delete
        category = Category.objects.create(
            name='Name 1',
            description='This is an old category.'
        )
        
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data for category deletion
        data = {
            'id': category.id,
        }
        
        # Send POST request to the product creation view
        response = self.client.post(self.delete_category_url, data)
        
        # Check if the response is a redirect or success
        self.assertTrue(response.status_code == status.HTTP_302_FOUND or response.status_code == status.HTTP_200_OK, f'status code: {response.status_code}')
        self.assertEqual(Category.objects.count(), 0)
        
    
    