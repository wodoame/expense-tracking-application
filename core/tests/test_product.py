from datetime import date
from authentication.models import User
from django.test import TestCase, Client
from core.tests.utils.product import create_random_product, create_random_products
ADD_PRODUCT_URL = '/implementations/dashboard/'
EDIT_PRODUCT_URL = '/implementations/dashboard/?edit=1'
DELETE_PRODUCT_URL = '/implementations/dashboard/?delete=1'
class TestProduct(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.client.login(username='testuser', password='testpass')
        
    def test_add_product(self):
        response = self.client.post(ADD_PRODUCT_URL, {
            'name': 'Test Product',
            'cedis': 10,
            'pesewas': 5,
            'description': 'Test Description',
            'date': date.today().isoformat(),
        })
        self.assertEqual(self.user.products.count(), 1)
        
    def test_edit_product(self):
        product = create_random_product(self.user)
        response = self.client.post(EDIT_PRODUCT_URL, {
            'id': product.id,
            'name': 'Updated Product',
            'cedis': 20,
            'pesewas': 0,
            'description': 'Updated Description',
            'date': product.date.isoformat(),
            'new-date': date.today().isoformat()
        })
        
        product.refresh_from_db()
        self.assertEqual(product.name, 'Updated Product')
        self.assertEqual(product.description, 'Updated Description')
        
    def test_delete_product(self):
        product = create_random_product(self.user)
        self.assertEqual(self.user.products.count(), 1) # Ensure product exists before deletion
        response = self.client.post(DELETE_PRODUCT_URL, {'id': product.id, 'date': product.date.isoformat()})
        self.assertEqual(self.user.products.count(), 0) # Ensure product is deleted
        
    def tearDown(self):
        self.client.logout()