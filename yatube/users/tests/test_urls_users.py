from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class URLTests(TestCase):
    """Класс для тестирования URL адресов приложения users"""

    @classmethod
    def setUpClass(cls):
        """Создать объект User в БД"""
        super().setUpClass()
        cls.test_user = User.objects.create(
            username='TestUser',
            password='Yaroslav1',
            first_name='Ivan',
            last_name='Ivanov',
            email='ivan777@yandex.ru',
        )

    def setUp(self):
        """Создать авторизованный клиент, словарь URL адресов и шаблонов"""
        # self.test_user = User.objects.create(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)
        self.templates_urls_1 = {
            # '/auth/logout/': 'users/logged_out.html',
            # '/auth/signup/': 'users/signup.html',
            # '/auth/login/': 'users/login.html',
            # '/auth/password_change/': 'users/password_change.html',
            # '/auth/password_change/done/': 'users/password_change_done.html',
            # '/auth/password_reset/': 'users/password_reset_form.html',
            # '/auth/password_reset/done/': 'users/password_reset_done.html',
            # '/auth/reset/<uidb64>/<token>/':
            #     'users/password_reset_confirm.html',
            'auth/reset/done/': 'users/password_reset_complete.html',
        }
        self.templates_urls_2 = {
            # '/auth/logout/': 'users/logged_out.html',
            # '/auth/signup/': 'users/signup.html',
            # '/auth/login/': 'users/login.html',
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            # '/auth/password_reset/': 'users/password_reset_form.html',
            # '/auth/password_reset/done/': 'users/password_reset_done.html',
            # '/auth/reset/<uidb64>/<token>/':
            #     'users/password_reset_confirm.html',
            # 'auth/reset/done/': 'users/password_reset_complete.html',
        }

    def test_urls_uses_correct_templates(self):
        for address, template in self.templates_urls_1.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
    #
    # def test_urls_2(self):
    #     for address, template in self.templates_urls_2.items():
    #         with self.subTest(address=address):
    #             response = self.authorized_client.get(address)
    #             self.assertTemplateUsed(response, template)

    # def test_urls_3(self):
    #     response = self.authorized_client.get('auth/reset/done/')
    #     self.assertTemplateUsed(response, 'users/password_reset_complete.html')
