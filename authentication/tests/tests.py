from django.test import TestCase, Client
from authentication.views import AuthCallback
from authentication.models import User
from authentication.schemas import UserModel, UserMetadata, AppMetadata
from unittest.mock import patch, MagicMock
from rest_framework import status
class CreateUserFromGoogleTest(TestCase):
    def setUp(self):
        self.auth_callback = AuthCallback()
        self.mocked_request = MagicMock()
        self.client = Client()
        self.user_data = UserModel(
            id='18b94c1e-21ed-42de-9605-dc1e617ad5c7',
            aud='authenticated',
            role='authenticated',
            email='testuser@gmail.com',
            email_confirmed_at=None,
            phone='',
            confirmed_at=None,
            last_sign_in_at=None,
            app_metadata=AppMetadata(provider='google', providers=['google']),
            user_metadata=UserMetadata(
                avatar_url=None,
                email='testuser@gmail.com',
                email_verified=True,
                full_name='Test User',
                iss=None,
                name='TestUser',
                phone_verified=False,
                picture=None,
                provider_id=None,
                sub=None
            ),
            identities=[],
            created_at=None,
            updated_at=None,
            is_anonymous=False
        )

    def test_create_user_from_google(self):
        user = self.auth_callback.create_user_from_google(self.user_data)
        self.assertIsInstance(user, User)
        self.assertEqual(user.email, 'testuser@gmail.com')
        self.assertEqual(user.first_name, 'Test User')
        self.assertEqual(user.username, 'testuser_google')
        self.assertFalse(user.has_usable_password())  # User created by oauth should have no usable password
    
    def test_signup_user_with_google_if_not_exists(self):
        data = {
            'user': self.user_data.model_dump()
        }
        response = self.client.post('/auth/callback/?action=signin', data=data, content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email=self.user_data.email).exists())
        self.assertTrue(User.objects.filter(username='testuser_google').exists())