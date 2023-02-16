from http import HTTPStatus
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, User, Group, Comment


class TestCreatePostForm(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Example group',
            slug='test-slug',
            description='Text of group'
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_new_post_in_BD(self):
        """После отправки валидной формы создается новая запись в БД"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Example text',
            'group': self.group.id,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': self.user.username}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text='Example text',
                        group=self.group.id,
                        author=self.user).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_correct(self):
        """Валидная форма редактирует пост при отправке
        со страницы редактирования поста"""
        self.post = Post.objects.create(
            author=self.user,
            text='Example text',
            group=self.group
        )
        self.group_1 = Group.objects.create(
            title='Group 1',
            slug='test1',
            description='test group 1'
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Change text',
            'group': self.group_1.id}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                             kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(text='Change text',
                        group=self.group_1.id,
                        author=self.user).exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_not_edit_if_guest_client(self):
        """Пост не изменяется, если пользователь - гость"""
        self.post = Post.objects.create(
            author=self.user,
            text='Example text',
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Text change'
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertFalse(Post.objects.filter(text='Text change').exists())
        self.assertEqual(response.status_code, HTTPStatus.OK)


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_guest_client(self):
        """Проверка, что гость не может оставлять коммент"""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент'}
        self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_comment_authorized_client(self):
        """Проверка публикации комментария от авторизованного пользователя"""
        comment_count = Comment.objects.count()
        form_data = {'text': 'Тестовый коммент'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse("posts:post_detail",
                              kwargs={"post_id": self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(text='Тестовый коммент').exists())
