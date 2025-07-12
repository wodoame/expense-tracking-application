from django.test import TestCase, Client
from authentication.models import User
from django.urls import reverse
from django.contrib.auth import authenticate
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime, date
from ..datechecker import get_activity_in_last_year
from core.tests.utils.product import create_random_products
from core.serializers import ProductSerializer


class DateCheckerTestCase(TestCase):
    """Base test case with common setup for datechecker tests"""
    
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


class GetActivityInLastYearTests(DateCheckerTestCase):
    @patch('core.utils.get_products_in_the_last_year', return_value=[])
    def test_get_activity_in_last_year_with_no_products(self, mock_get_products):
        activities = get_activity_in_last_year(self.mock_request)
        self.assertEqual(len(activities), 12)
        
    @patch('core.utils.get_products_in_the_last_year')
    def test_get_activity_in_last_year_with_products(self, mock_get_products):
        products = ProductSerializer(create_random_products(self.user, 5), many=True).data
        mock_get_products.return_value = products
        activities = get_activity_in_last_year(self.mock_request)
        self.assertEqual(len(activities), 12)