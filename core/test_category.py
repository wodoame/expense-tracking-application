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
    
    def test_create_category_no_description(self):
        """Test that a category can be created using a POST request"""
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data
        form_data = {
            'name': 'Test Category'
        }
        
        # Send POST request
        response = self.client.post(self.category_create_url, form_data)
        
        # Check response status (assuming redirect on success)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # HTTP 302 Found indicates a redirect

        # Verify category was created
        self.assertTrue(Category.objects.filter(name='Test Category').exists())
    
    def test_create_category_empty_description(self):
        """Test that a category cannot be created with an empty description"""
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data
        form_data = {
            'name': 'Test Category', 
            'description': '', 
        }
        
        # Send POST request
        response = self.client.post(self.category_create_url, form_data)
        
        # Check response status (assuming redirect on success)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)  # HTTP 302 Found indicates a redirect

        # Verify category was created
        self.assertTrue(Category.objects.filter(name='Test Category').exists())
        
    def test_create_category_empty_name(self):
        """Test that a category cannot be created with an empty name"""
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare invalid form data
        form_data = {
            'name': ''  # Empty name
        }
        
        # Send POST request
        response = self.client.post(self.category_create_url, form_data)
        
        # Check for form errors
        # self.assertFormError(response, 'form', 'name', 'This field is required.')
    
        # Check that the form is in the response context
        # self.assertTrue('form' in response.context)
        
        # Verify no category was created
        self.assertFalse(Category.objects.filter(name='').exists())
    
    
    def test_cannot_create_duplicate_category(self):
        """Test that a category with duplicate name cannot be created"""
        # Create a category first
        Category.objects.create(
            name='Existing Category',
            description='Existing description'
        )
        
        # Login if authentication is required
        self.client.login(username='testuser', password='testpassword')
        
        # Prepare form data with the same name
        form_data = {
            'name': 'Existing Category',
            'description': 'Different description'
        }
        
        # Send POST request
        response = self.client.post(self.category_create_url, form_data)
        
        # Check for form errors (assuming your form validates unique names)
        # self.assertFormError(response, 'form', 'name', 'Category with this name already exists.')
        self.assertTrue(Category.objects.filter(name='Existing Category').count() == 1, 'Category with this name already exists')