from django.test import TestCase, Client


class TestTemplatesCore(TestCase):
    def test_unexisting_page(self):
        """Получить ошибку при запросе несуществущего URL"""
        self.guest_client = Client()
        response = self.guest_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
