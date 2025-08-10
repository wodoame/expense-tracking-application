from django.test import TestCase, Client
from core.serializers import ProductSerializer
from core.models import Product, User, Category
from core.utils import groupByDate
from django.test import Client
from core.tests.utils.product import create_random_products
from core.utils import EnhancedExpensePaginator
from unittest.mock import MagicMock
from django.utils import timezone
from urllib.parse import quote
class Tests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.user.date_joined = timezone.make_aware(timezone.datetime(2025, 1, 1)) # assume the user has been created a long time ago
        self.user.save()
        self.client = Client()
        self.mocked_request = MagicMock()
        self.mocked_request.user = self.user
        self.client.login(username='testuser', password='testpass123')
        
    def test_group_products_by_date(self):
        create_random_products(self.user, count=10)
        products = ProductSerializer(
            Product.objects.all(), 
            many=True
        ).data # serializer products
        records = groupByDate(products)
        # a record is a day with a list of products bought on that day 
        # ( For example {'date': '2025-06-09',
        # 'products': [{'id': 6, 'category': None, 'name': 'Butter', 'description': 'Gluten free.', 'price': 2.97, 'date': '2025-06-09T19:18:27.769728Z', 'user': 1, 'date_for_grouping': '2025-06-09'}], 'total': 2.97})
        number_of_products_grouped = 0
        for record in records:
            number_of_products_grouped += len(record['products'])
            
        # check if the number of products in the grouped records is equal to the total number of products passed to the function
        self.assertEqual(len(products), number_of_products_grouped)
    
    def test_expense_paginator_returns_all_expenses(self):
        expenses_created = 20
        create_random_products(self.user, count=expenses_created)
        paginator = EnhancedExpensePaginator(self.mocked_request, cache_key=f'records-{self.user.username}')
        total_pages = paginator.get_total_pages()
        number_of_expenses = 0
        
        # get all pages and see if all products are returned
        # this is to ensure that the paginator works correctly
        for page in range(1, total_pages + 1): # NOTE: a page may consist of many days; The paginator paginates by number of days
            url = f'/components/records/?page={page}'
            response = self.client.get(url)
            days = response.context['items'] # also called records
            
            # check the number of products bought on each day
            for day in days:
                number_of_expenses += len(day.get('products'))
        
        self.assertEqual(number_of_expenses, expenses_created)  # check if the total number of products is equal to the number of products created

    def test_expense_paginator_returns_all_expenses_in_specific_category(self):
        category = Category.objects.create(user=self.user, name='Test Category')
        expenses_created = 20
        create_random_products(self.user, count=expenses_created, category=category)
        create_random_products(self.user, count=15) # no category specified, so it will be None
        paginator = EnhancedExpensePaginator(
                self.mocked_request,
                cache_key=f'{quote(category.name)}-records-{self.user.username}',
                specific_category=True, 
                category_name=category.name,
                extra_filters={'category__name': category.name}
                )
        total_pages = paginator.get_total_pages()
        number_of_expenses = 0

        # get all pages and see if all products in the specified category are returned
        # this is to ensure that the paginator works correctly
        for page in range(1, total_pages + 1): # NOTE: a page may consist of many days; The paginator paginates by number of days
            url = f'/components/records/?page={page}&oneCategory=1&categoryName={category.name}'
            response = self.client.get(url)
            days = response.context['items'] # also called records

            # check the number of products bought on each day
            for day in days:
                number_of_expenses += len(day.get('products'))

        self.assertEqual(number_of_expenses, expenses_created)  # check if the total number of products is equal to the number of products created