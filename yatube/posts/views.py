from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Post, Group, Follow
from .forms import PostForm, CommentForm
from .utils import paginator_func

User = get_user_model()


# Главная страница
def index(request):
    post_list = (Post.objects.select_related('author', 'group')
                 .all())
    page_obj = paginator_func(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


# Страница с группами
def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = (group.posts.select_related('author')
                 .all())
    page_obj = paginator_func(request, post_list)
    context = {'group': group,
               'page_obj': page_obj, }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = (author.posts.select_related('group')
                 .all())
    page_obj = paginator_func(request, post_list)
    following = (author.following.filter(user=request.user.id).exists()
                 and request.user.is_authenticated)
    context = {'author': author,
               'page_obj': page_obj,
               'following': following}
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    form = CommentForm(request.POST or None)
    post = get_object_or_404(Post.objects.select_related('author', 'group'),
                             id=post_id)
    comments = post.comments.all()
    context = {'post': post,
               'form': form,
               'comments': comments}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', username=request.user)
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:profile', username=request.user)
    form = PostForm(request.POST or None,
                    files=request.FILES or None,
                    instance=post)
    if form.is_valid():
        post = form.save()
        post.save()
        return redirect('posts:post_detail', post_id)
    return render(request, 'posts/create_post.html', {'form': form,
                                                      'is_edit': True})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Отображение страницы с подписками"""
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator_func(request, posts)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Функция подписки на автора
    """
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:follow_index')


@login_required
def profile_unfollow(request, username):
    """Функция отписки от автора
    """
    author = get_object_or_404(User, username=username)
    if author.following.filter(user=request.user).exists():
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:follow_index')
