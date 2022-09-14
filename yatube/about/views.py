from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View класс страницы об авторе"""

    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """View класс страницы о технологиях"""

    template_name = 'about/tech.html'
