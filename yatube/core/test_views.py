from django.contrib.auth import get_user_model
from django.test import Client, TestCase


User = get_user_model()


class CoreURLTests(TestCase):
    """Класс для тестирования URL адресов приложения core"""

    @classmethod
    def setUpClass(cls):
        """Создать объект пользователя."""
        super().setUpClass()
        cls.user = User.objects.create(username='TestAuthor')

    def setUp(self):
        """
        Создать 3 клиента: неавторизованного, авторизованного и
        авторизованного автора поста.
        """
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_404_page(self):
        """
        Проверить что страница 404 отдаёт кастомный шаблон.
        """
        response = self.authorized_client.get('/unexisting_page/')
        self.assertTemplateUsed(response, 'core/404.html')
