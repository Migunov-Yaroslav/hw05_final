from django.test import TestCase

from ..constants import POST_TEXT_STR
from ..models import Group, Post, User


class PostModelTest(TestCase):
    """Класс для тестирования модели Post."""

    @classmethod
    def setUpClass(cls):
        """Создать объекты пользователя, группы, поста для тестовой БД."""
        super().setUpClass()
        cls.user = User.objects.create(username='test_auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст. Он нужен подлиннее, чтобы проверить, '
                 'что метод __str__ оставляет только 15 символов',
            group=cls.group,
            author=cls.user,
        )

    def test_method_str(self):
        """
        Проверить метод __str__ модели.
        Метод __str__ должен возвращать первые 15 символов поста.
        """
        post = self.post
        expected_object_str = post.text[:POST_TEXT_STR]
        self.assertEqual(expected_object_str, str(post))

    def test_help_text(self):
        """Проверить help_text полей модели на ожидаемые значения"""
        post = self.post
        fields_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }
        for value, expected in fields_help_texts.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected,
                )

    def test_verbose_name(self):
        """Проверить verbose name полей модели на ожидаемые значения."""
        post = self.post
        fields_verbose_names = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'group': 'Группа',
            'author': 'Автор',
        }
        for value, expected in fields_verbose_names.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected,
                )


class GroupTest(TestCase):
    """Класс для тестирования модели Group"""

    @classmethod
    def setUpClass(cls):
        """Создать объекты группы для тестовой БД."""
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )

    def test_method_str(self):
        """Проверить метод __str__ модели.
        Метод __str__ должен возвращать значение поля title"""
        group = self.group
        expected_object_str = group.title
        self.assertEqual(expected_object_str, str(group))
