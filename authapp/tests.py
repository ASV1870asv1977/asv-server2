from django.test import TestCase
from django.test.client import Client

from authapp.models import ShopUser
from geekshop import settings


class UserAuthTestCase(TestCase):
    status_code_success = 200
    status_code_redirect = 302
    status_code_success_redirect = 301
    status_code_forbidden = 403
    username = 'django2'
    user_password = 'geekbrains'

    def setUp(self):
        self.client = Client()

        self.user = ShopUser.objects.create_user(
            username=self.username,
            email='django2@gb.local',
            password=self.user_password,
        )

    def test_login_user(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertNotContains(response, 'Пользователь', status_code=self.status_code_success_redirect)

        self.client.login(username=self.username, password=self.user_password)
        user_data = {
            'username': self.username,
            'password': self.user_password,
        }

        response = self.client.post('/auth/login/', data=user_data)
        self.assertEqual(response.status_code, self.status_code_redirect)

        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertFalse(response.context['user'].is_anonymous)
        self.assertNotContains(response, 'Пользователь', status_code=self.status_code_success)

    def test_register_user(self):
        new_user_data = {
            'username': 'django3',
            'email': 'django3@gb.local',
            'password1': self.user_password,
            'password2': self.user_password,
            'age': '33'
        }

        response = self.client.post('/auth/register/', data=new_user_data)
        self.assertEqual(response.status_code, self.status_code_redirect)

        new_user = ShopUser.objects.get(username=new_user_data['username'])

        activation_url = f'{settings.DOMAIN}/auth/verify/{new_user_data["email"]}/{new_user.activation_key}'

        response = self.client.get(activation_url)
        self.assertEqual(response.status_code, self.status_code_success)

        response = self.client.get('/')
        self.assertEqual(response.status_code, self.status_code_success)
        self.assertNotContains(response, 'Пользователь', status_code=self.status_code_success)

