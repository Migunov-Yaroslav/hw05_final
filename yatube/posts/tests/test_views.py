import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User
from ..constants import POSTS_ON_PAGE


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTest(TestCase):
    """Класс для тестирования view-функций приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создать объекты пользователя, группы, поста для тестовой БД."""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.user_2 = User.objects.create(username='TestAuthor2')
        cls.user_3 = User.objects.create(username='TestAuthor3')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-group-2',
            description='Описание тестовой группы 2',
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
        cls.post = Post.objects.create(
            text='Тестовый пост',
            group=cls.group,
            author=cls.user,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user,
        )
        cls.follow = Follow.objects.create(user=cls.user, author=cls.user_3)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        """Создает авторизованного пользователя"""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.user_2)
        self.fields = ('id', 'text', 'group', 'author', 'image')
        cache.clear()

    def test_views_uses_correct_templates(self):
        """Проверить, что view-функции используют верные шаблоны."""
        templates_urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user.username}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}):
                'posts/create_post.html',
        }
        for reverse_name, template in templates_urls.items():
            with self.subTest(url=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_view_index(self):
        """
        Проверить view-функцию index.
        В словаре context должны содержаться объекты Post с соответствующими
        полями.
        """
        response = self.authorized_client.get(reverse('posts:index'))
        for element in response.context.get('page_obj'):
            with self.subTest(element=element):
                self.assertIsInstance(element, Post)
        for field in self.fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get('page_obj')[0], field),
                    getattr(self.post, field),
                )

    def test_view_group_list(self):
        """
        Проверить view-функцию group_list.
        В словаре context должны содержаться объекты Post с соответствующими
        полями. Группа каждого поста должна совпадать с группой,
        содержащейся в словаре context.
        """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug},
        ))

        for element in response.context.get('page_obj').object_list:
            with self.subTest(element=element):
                self.assertIsInstance(element, Post)
                self.assertEqual(
                    element.group,
                    response.context.get('group'),
                )
        for field in self.fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get('page_obj')[0], field),
                    getattr(self.post, field),
                )

    def test_view_profile(self):
        """
        Проверить view-функцию profile.
        В словаре context должны содержаться объекты Post с соответствующими
        полями. Автор каждого поста должен совпадать с автором,
        содержащимся в словаре context. В словаре context должна содержаться
        переменная булевского типа following = False, поскольку
        авторизованный клиент делает запрос к своему профайлу.
        """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': self.user.username},
        ))
        for element in response.context.get('page_obj').object_list:
            with self.subTest(element=element):
                self.assertIsInstance(element, Post)
                self.assertEqual(
                    element.author,
                    response.context.get('author'),
                )
        for field in self.fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get('page_obj')[0], field),
                    getattr(self.post, field),
                )
        self.assertIsInstance(response.context.get('following'), bool)
        self.assertFalse(response.context.get('following'))

    def test_view_post_detail(self):
        """
        Проверить view-функцию post_detail.
        В словаре context должны содержаться
        - один объект Post с соответствующими полями, созданный
        пользователем с заданным id;
        - список объектов Comment, относящихся к этому посту;
        - форма для создания комментария к посту.
        """
        response = self.authorized_client.get(reverse(
            'posts:post_detail', kwargs={'post_id': self.post.id},
        ))
        form_fields = {'text': forms.fields.CharField}
        for field in self.fields:
            with self.subTest(field=field):
                self.assertEqual(
                    getattr(response.context.get('post'), field),
                    getattr(self.post, field),
                )
        for element in response.context.get('comments'):
            with self.subTest(element=element):
                self.assertIsInstance(element, Comment)
        for element in response.context.get('comments'):
            with self.subTest(element=element):
                self.assertEqual(
                    element.post,
                    response.context.get('post'),
                )
        self.assertIsInstance(
            response.context.get('form').fields.get('text'),
            form_fields['text'],
        )

    def test_view_post_create(self):
        """
        Проверить view-функцию post_create.
        В словаре context должна содержаться форма для создания поста.
        """
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_view_post_edit(self):
        """
        Проверить view-функцию post_edit.
        В словаре context должна содержаться форма редактирования поста с
        заданным id. У формы должен быть инстанс редактируемого поста. В
        словаре context должен содержаться переменная булевского типа
        is_edit = True.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id},
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

        self.assertEqual(
            response.context.get('form').instance.id, self.post.id,
        )
        self.assertIsInstance(response.context.get('is_edit'), bool)
        self.assertTrue(response.context.get('is_edit'))

    def test_creation_post_redirect(self):
        """
        Проверить появление нового поста на страницах index, group_list,
        profile при его создании на странице post_create.
        После создания нового поста должен происходить редирект на страницу
        profile.
        """
        urls = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        )
        test_post = Post.objects.create(
            text='Текст поста для функции test_creation_post_correct',
            group=self.group,
            author=self.user,
        )

        for address in urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(
                    response.context.get('page_obj')[0], test_post,
                )

    def test_no_new_posts_in_other_groups(self):
        """
        Проверить, что новый пост не попадает на страницу группы,
        к которой не принадлежит.
        """
        test_post_2 = Post.objects.create(
            text='Текст поста для функции test_creation_post_correct',
            group=self.group,
            author=self.user,
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_2.slug}),
        )
        self.assertNotIn(
            test_post_2, response.context.get('page_obj').object_list,
        )

    def test_cache_index(self):
        """Проверить кэширование списка постов на главной странице."""
        response_initial = self.authorized_client.get(reverse(
            'posts:index'))
        posts_initial = response_initial.content

        Post.objects.create(text='Тест кеша.', author=self.user)

        response_after_create = self.authorized_client.get(reverse(
            'posts:index'))
        posts_after_create = response_after_create.content

        self.assertEqual(posts_initial, posts_after_create)

        cache.clear()

        response_after_clear_cache = self.authorized_client.get(reverse(
            'posts:index'))
        posts_after_clear_cache = response_after_clear_cache.content
        self.assertNotEqual(posts_after_create, posts_after_clear_cache)

    def test_follow_possibility(self):
        """Проверить возможность подписаться на автора только 1 раз."""
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user_2,
        ))
        following_count_before = self.user.follower.count()
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}
        ))
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username}
        ))
        following_count_after = self.user.follower.count()
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user_2,
        ))
        self.assertEqual(following_count_after, following_count_before + 1)

    def test_unfollow_possibility(self):
        """Проверить возможность отписаться от автора."""
        self.assertTrue(Follow.objects.filter(
            user=self.user,
            author=self.user_3,
        ))
        following_count_before = self.user.follower.count()
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_3.username}
        ))
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_2.username}
        ))
        self.assertFalse(Follow.objects.filter(
            user=self.user,
            author=self.user_3,
        ))
        following_count_after = self.user.follower.count()
        self.assertEqual(following_count_after, following_count_before - 1)

    def test_follow_creates_for_right_page(self):
        """
        Проверить появление новой записи автора в лентах подписанных на
        него пользователей.
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username, }
        ))
        new_post = Post.objects.create(
            text='Тестовый пост3',
            group=self.group,
            author=self.user_2,
            image=self.uploaded,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(
            new_post,
            response.context.get('page_obj').object_list,
        )

    def test_follow_dont_creates_for_wrong_page(self):
        """
        Проверить отсутствие записи автора в лентах не подписанных на
        него пользователей
        """
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_2.username, }
        ))
        new_post = Post.objects.create(
            text='Тестовый пост3',
            group=self.group,
            author=self.user_2,
            image=self.uploaded,
        )
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertNotIn(
            new_post,
            response.context.get('page_obj').object_list,
        )


class PaginatorViewsTest(TestCase):
    """Класс для тестирования паджинатора приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создать объекты пользователя, группы, поста для тестовой БД."""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        posts = [
            Post(
                text='Тестовый текст',
                group=cls.group,
                author=cls.user,
            ) for i in range(0, 11)
        ]
        Post.objects.bulk_create(posts)

    def setUp(self):
        """Создает авторизованного пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )

    def test_paginator_first_page(self):
        """
        Проверить первую страницу паджинатора для страниц index, group_list,
        profile.
        На странице должно выводиться 10 постов.
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
        Проверить вторую страницу паджинатора для страниц index, group_list,
        profile.
        На странице должны выводиться оставшиеся посты.
        """
        for address in self.urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address + '?page=2')
                self.assertEqual(
                    len(response.context['page_obj']),
                    Post.objects.count() - POSTS_ON_PAGE,
                )
