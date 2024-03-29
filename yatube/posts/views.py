from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginator_func


def index(request):
    """Отобразить главную страницу."""
    post_list = Post.objects.select_related('author', 'group')
    context = {'page_obj': paginator_func(request, post_list)}

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """Отобразить страницу с сообщениями сообщества."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author')
    context = {'page_obj': paginator_func(request, post_list), 'group': group}

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """Отобразить страницу пользователя."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group')
    following = True if (
        request.user.is_authenticated and Follow.objects.filter(
            user=request.user,
            author=author,
        )
    ) else False
    context = {
        'page_obj': paginator_func(request, post_list),
        'author': author,
        'following': following,
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """Отобразить страницу просмотра поста."""
    post = get_object_or_404(Post, id=post_id)
    comments_list = post.comments.select_related('author')
    form = CommentForm(request.POST or None)
    context = {'post': post, 'comments': comments_list, 'form': form}

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Отобразить страницу создания поста."""
    form = PostForm(request.POST or None, files=request.FILES or None)
    context = {'form': form}
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()

        return redirect('posts:profile', username=request.user.username)

    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    """Отобразить страницу редактирования поста."""
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    is_edit = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    context = {'form': form, 'is_edit': is_edit}
    if form.is_valid():
        form = form.save(commit=False)
        form.author = request.user
        form.save()

        return redirect('posts:post_detail', post_id=post_id)

    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    """Создать комментарий"""
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
    """
    Отобразить страницу с постами авторов, на которых подписан
    пользователь.
    """
    all_authors_posts = Post.objects.filter(
        author__following__user=request.user
    )
    context = {'page_obj': paginator_func(request, all_authors_posts)}

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Создать подписку на автора."""
    author = get_object_or_404(User, username=username)
    if author != request.user and not Follow.objects.filter(
            user=request.user,
            author=author,
    ).exists():
        Follow.objects.create(user=request.user, author=author)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    """Удалить подписку на автора."""
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()

    return redirect('posts:profile', username=username)
