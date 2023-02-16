from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200,
                             verbose_name='Название группы')
    slug = models.SlugField(unique=True,
                            verbose_name='Короткая ссылка')
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Напишите ваш пост в этом окне')
    # pub_date = models.DateTimeField(auto_now_add=True,
    #                                 verbose_name='Дата и время публикации')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        Group,
        related_name='posts',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Группа, к которой относится пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )
    # Аргумент upload_to указывает директорию,
    # в которую будут загружаться пользовательские файлы.

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        related_name='comments',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    author = models.ForeignKey(
        User,
        related_name='comments',
        on_delete=models.CASCADE,
    )
    text = models.TextField(verbose_name='Текст комментария',
                            help_text='Напишите ваш комментарий в этом окне')
    # created = models.DateTimeField(auto_now_add=True,
    #                                 verbose_name='Дата и время публикации')

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text


class Follow(models.Model):
    """Модель подписчиков
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following')
