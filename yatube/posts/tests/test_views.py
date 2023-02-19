from . import TestCaseWithTmpMedia
from django.urls import reverse
from django import forms
from django.core.cache import cache
from django.test import TestCase, Client
from django.core.files.uploadedfile import SimpleUploadedFile
from ..models import Post, Group, User, Follow
from ..utils import POST_RESTRICTION

COUNT_OF_POST = 13
# TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Example group',
            slug='test-slug',
            description='Text of group'
        )
        posts = list()
        for i in range(COUNT_OF_POST):
            posts.append(Post(text=f'Текст с номером {i}',
                              group=cls.group,
                              author=cls.user))
        Post.objects.bulk_create(posts)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Первая страница отоюражает 10 постов"""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POST_RESTRICTION)

    def test_second_page_contains_three_records(self):
        """На второй странице оставшиеся 3 поста"""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']),
                         COUNT_OF_POST - POST_RESTRICTION)


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Example group',
            slug='test-slug',
            description='Text of group'
        )
        cls.post = Post.objects.create(author=cls.user,
                                       text='Example text',
                                       group=cls.group)
        cls.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': cls.group.slug}):
            'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': cls.post.author}):
            'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': cls.post.id}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': cls.post.id}):
            'posts/create_post.html'}

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_correct_template(self):
        """URL-адреса соответсвуют шаблонам"""
        for address, template in self.templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_group_list_context(self):
        """Проверка context в шаблоне с постами группы"""
        response = self.guest_client.get(reverse('posts:group_list',
                                         kwargs={'slug': self.group.slug}))
        expected = Post.objects.filter(group=self.group)
        self.assertCountEqual(response.context['page_obj'], expected)

    def test_profile_context(self):
        """Проверка context в шаблоне профиля пользователя"""
        response = self.guest_client.get(reverse('posts:profile',
                                         args=(self.post.author,)))
        expected = Post.objects.filter(author=self.user)
        self.assertCountEqual(response.context.get('page_obj'), expected)

    def test_post_detail_context(self):
        """Проверка context в шаблоне деталей поста"""
        response = self.guest_client.get(reverse('posts:post_detail',
                                         kwargs={'post_id': self.post.id}))
        self.assertEqual(response.context.get('post').text, self.post.text)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_create_post_context(self):
        """Проверка context в шаблоне создания поста"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_context(self):
        """Проверка context в шаблоне редактирования поста"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_of_group_in_correct_pages(self):
        """Проверка отображения поста на страницах"""
        pages = {
            reverse('posts:index'): Post.objects.get(group=self.post.group),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}):
                    Post.objects.get(group=self.post.group),
            reverse('posts:profile', kwargs={'username': self.post.author}):
                    Post.objects.get(group=self.post.group)
        }
        for value, expected in pages.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertIn(expected, form_field)

    def test_post_not_in_another_group(self):
        """Проверка принадлежности поста только выбранной группе
           (не попадает в другую группу)"""
        page = {
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                Post.objects.exclude(group=self.post.group)
        }
        for value, expected in page.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                form_field = response.context['page_obj']
                self.assertNotIn(expected, form_field)

    def test_cache(self):
        """Проверка кеширования
        """
        page1 = (self.guest_client.get(reverse('posts:index'))).content
        Post.objects.get(id=1).delete()
        page2 = (self.guest_client.get(reverse('posts:index'))).content
        self.assertEqual(page1, page2)

    def test_follow(self):
        """Проверка работы подписок на авторов"""
        response = self.authorized_client.get(reverse('posts:follow_index'))
        # Проверка отсутствия подписок
        self.assertEqual(len(response.context['page_obj']), 0)
        Follow.objects.get_or_create(user=self.user, author=self.post.author)
        response2 = self.authorized_client.get(reverse('posts:follow_index'))
        # Подписка появилась
        self.assertEqual(len(response2.context['page_obj']), 1)
        self.assertIn(self.post, response2.context['page_obj'])
        user2 = User.objects.create(username='Another user')
        self.authorized_client2 = Client()
        self.authorized_client2.force_login(user2)
        response3 = self.authorized_client2.get(reverse('posts:follow_index'))
        # Подписка не появилась у другого пользователя
        self.assertNotIn(self.post, response3.context["page_obj"])
        Follow.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        # После отписки посты исчезли у пользователя
        self.assertEqual(len(response.context['page_obj']), 0)


# @override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsImageTests(TestCaseWithTmpMedia):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='NoName')
        cls.group = Group.objects.create(
            title='Example group',
            slug='test-slug',
            description='Text of group'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(author=cls.user,
                                       image=cls.uploaded,
                                       text='Example text',
                                       group=cls.group)

    # @classmethod
    # def tearDownClass(cls):
    #     super().tearDownClass()
    #     shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()

    def test_post_with_image_in_BD(self):
        """Проверка, что пост с картинкой сохраняется в БД"""
        self.assertTrue(
            Post.objects.filter(text='Example text',
                                image='posts/small.gif').exists())

    def test_post_in_index_profile_group_list(self):
        """Проверка изображения для 3 страниц"""
        templates = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.post.author})
        )
        for address in templates:
            with self.subTest(address):
                response = self.guest_client.get(address)
                obj = response.context['page_obj'][0]
                self.assertEqual(obj.image, self.post.image)

    def test_post_in_post_detail(self):
        """Проверка изображения для пост дитейл"""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        obj = response.context['post']
        self.assertEqual(obj.image, self.post.image)
