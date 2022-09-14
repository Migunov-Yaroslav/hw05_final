from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """
    Класс формы сообщения.

    Используется в шаблоне create_post.html на страницах создания и
    редактирования поста.
    """

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    """
    Класс формы комментария.

    Используется в шаблоне post_detail.html.
    """

    class Meta:
        model = Comment
        fields = ('text',)
