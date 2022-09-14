from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..constants import POSTS_ON_PAGE

User = get_user_model()


class PaginatorViewsTest(TestCase):
    """Класс для тестирования view функций приложения posts"""

    @classmethod
    def setUpClass(cls):
        """Создает запись в БД"""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        for cls.elem in (
                'post1', 'post2', 'post3', 'post4', 'post5', 'post6', 'post7',
                'post8', 'post9', 'post10', 'post11',
        ):
            cls.elem = Post.objects.create(
                text='Тестовый текст',
                group=cls.group,
                author=cls.user,
            )

    def setUp(self):
        """Создает авторизованного пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(PaginatorViewsTest.user)
        self.urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PaginatorViewsTest.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PaginatorViewsTest.user.username},
            ),
        )

    def test_paginator_first_page(self):
        """
        Проверяет паджинатор на первой странице страниц index,
        group_list, profile
        """
        for address in self.urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    len(response.context['page_obj']),
                    POSTS_ON_PAGE,
                )

    def test_paginator_second_page(self):
        """
        Проверяет паджинатор на второй странице страниц index,
        group_list, profile
        """
        for address in self.urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    Post.objects.count() - POSTS_ON_PAGE,
                )
