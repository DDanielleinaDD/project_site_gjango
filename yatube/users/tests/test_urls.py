from http import HTTPStatus
from django.test import Client, TestCase


class TestUrlSignUp(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_signup_available(self):
        """Проверка доступа к регистрации любого посетителя"""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_correct_template(self):
        """URl получает нужный шаблон"""
        templates_url_names = {
            '/auth/signup/': 'users/signup.html'
        }
        for url, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
