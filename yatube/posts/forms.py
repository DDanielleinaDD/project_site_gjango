from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {'text': {'required': 'Текст поста обязателен!'}}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
