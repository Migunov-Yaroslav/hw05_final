from django.contrib import admin

from .models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """
    Класс сообщения для админки.

    Предназначен для настройки страницы администрирования проекта.
    """

    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    """
    Класс сообщества для админки.

    Предназначен для настройки страницы администрирования
    """

    list_display = (
        'pk',
        'title',
        'description',
    )
    search_fields = ('description',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


@admin.register(Comment)
class Comment(admin.ModelAdmin):
    """Класс предназначен для хранения информации о комментарии к посту."""

    list_display = (
        'pk',
        'text',
        'author',
        'post',
        'created',
    )
    list_editable = ('post',)
    search_fields = ('text',)
    list_filter = ('created',)
    empty_value_display = '-пусто-'


@admin.register(Follow)
class Follow(admin.ModelAdmin):
    """Класс предназначен для хранения информации о подписках пользователей."""

    list_display = (
        'pk',
        'user',
        'author',
    )
    list_editable = ('author',)
    search_fields = ('author',)
    list_filter = ('user',)
    empty_value_display = '-пусто-'
