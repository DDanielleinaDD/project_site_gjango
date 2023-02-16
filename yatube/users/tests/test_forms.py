from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class TestFormSignUp(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_signup(self):
        """Проверка работоспособности регистрации нового юзера"""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'User',
            'last_name': 'Userovich',
            'username': 'TestUser',
            'email': 'test@email.com',
            'password1': 'TestPass1',
            'password2': 'TestPass1'
        }
        response = self.guest_client.post(
            reverse('users:signup'), data=form_data, follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertEqual(response.status_code, HTTPStatus.OK)
