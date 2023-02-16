from http import HTTPStatus
from django.test import TestCase, Client


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_page_status(self):
        """Проверка состояния страниц"""
        templates = ['/about/author/', '/about/tech/']
        for address in templates:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_url_templates(self):
        """Проверка использования необходимых шаблонов"""
        templates = {
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html'
        }
        for address, template in templates.items():
            with self.subTest(template=template):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)
