from django.contrib.auth import get_user_model
from django.db import models

from .constants import POST_TEXT_STR

User = get_user_model()


class Group(models.Model):
    """
    Класс сообщества.

    Предназначен для хранения всей информации о сообществе.
    """

    title = models.CharField(max_length=200, verbose_name='Название группы')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Адрес страницы группы',
    )
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Класс сообщения.

    Предназначен для хранения всей информации о сообщении.
    """

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        help_text='Изображение к посту',
    )

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:POST_TEXT_STR]


class Comment(models.Model):
    """
    Класс комментария.

    Предназначен для хранения информации о комментарии к посту.
    """

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
        help_text='Пост, к которому будет относиться комментарий',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-created',)

    def __str__(self):
        return self.text[:POST_TEXT_STR]


class Follow(models.Model):
    """
    Класс подписки на автора.

    Предназначен для хранения информации об id подписавшегося пользователя
    (user) и id пользователя, на которого подписались (author).
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        help_text='Подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
        help_text='Заинтересовавший автор',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('-author',)
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_follow',
            ),
        ]
