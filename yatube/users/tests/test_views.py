from django.test import TestCase, Client
from django.urls import reverse


class TestViews(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_template(self):
        """Проверка использования нужного шаблона"""
        response = self.guest_client.get(reverse('users:signup'))
        self.assertTemplateUsed(response, 'users/signup.html')
