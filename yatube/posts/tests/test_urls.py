from http import HTTPStatus
from django.test import TestCase, Client

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.post = Post.objects.create(
            text='Example text',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Example group',
            slug='test-slug',
            description='Text of group'
        )
        cls.templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'}

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """Проверка шаблонов и связанных адресов"""
        for address, template in self.templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_create_page_for_redirect_if_anonymous(self):
        """Проверка редиректа, если неавторизованный пользователь
           по приватным URl лазит"""
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(response, '/auth/login/?next=/create/')

    def test_unexisting_page(self):
        """Получить ошибку при запросе несуществущего URL"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
