from http import HTTPStatus

from django.test import Client, TestCase

from ..models import Group, Post, User


class PostsURLTest(TestCase):
    """Класс для тестирования URL адресов приложения posts."""

    @classmethod
    def setUpClass(cls):
        """Создать объекты пользователя, группы, поста для тестовой БД."""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')
        cls.user_2 = User.objects.create(username='TestAuthor_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-group',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user,
        )

    def setUp(self):
        """
        Создать 3 клиента: неавторизованного, авторизованного и
        авторизованного автора поста.
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user_2)

        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_posts_urls_access_for_anonymous_user(self):
        """
        Проверить доступность страниц приложения posts для
        неавторизованного пользователя.
        Страница должны вернуть код 200 или 302.
        """
        urls_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/create/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/edit/': HTTPStatus.FOUND,
            f'/posts/{self.post.id}/comment/': HTTPStatus.FOUND,
            f'/profile/{self.user.username}/follow/': HTTPStatus.FOUND,
            f'/profile/{self.user.username}/unfollow/': HTTPStatus.FOUND,
            '/follow/': HTTPStatus.FOUND,
        }
        for address, status in urls_status.items():
            with self.subTest(url=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status)

    def test_posts_urls_correct_templates(self):
        """
        Проверить использование верных шаблонов для авторизованного
        автора поста на всех страницах приложения.
        """
        templates_urls = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_urls.items():
            with self.subTest(url=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_posts_redirect_for_anonymous_user(self):
        """
        Проверить корректность редиректа для анонимного пользователя на
        страницах создания поста и редактирования поста.
        """
        redirects_urls = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
                f'/auth/login/?next=/posts/{self.post.id}/edit/',
            f'/posts/{self.post.id}/comment/':
                f'/auth/login/?next=/posts/{self.post.id}/comment/'
        }
        for target_url, redirect_url in redirects_urls.items():
            with self.subTest(url=target_url):
                response = self.client.get(target_url, follow=True)
                self.assertRedirects(response, redirect_url)

    def test_post_edit_url(self):
        """
        Проверить корректность редиректа для пользователя, не являющегося
        автором поста, на странице редактирования этого поста.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/', follow=True,
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_posts_unexisting_page(self):
        """
        Проверить результат запроса к несуществующей странице.
        Должен возвращаться код 404.
        """
        response = self.authorized_client.get('/some-unexisting-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
