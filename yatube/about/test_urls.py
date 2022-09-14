from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class AboutURLTests(TestCase):
    """Класс для тестирования URL адресов приложения about"""

    def test_about_urls_for_anonymous_user(self):
        """
        Проверить доступность страниц.
        При запросе к странице должен возвращаться код 200.
        """
        urls_status = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK,
        }
        for address, status in urls_status.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, status.value)

    def test_about_urls_correct_templates(self):
        """
        Проверить использование правильных шаблонов для рендера
        соответствующих страниц.
        """
        templates_urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for address, template in templates_urls.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(response, template)
