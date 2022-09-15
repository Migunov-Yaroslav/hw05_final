from django.urls import path

from . import views


app_name = 'about'

"""
Список URL приложения about:
- author/ - информация об авторе;
- tech/ - информация об использованных технологиях.
"""
urlpatterns = [
    path('author/', views.AboutAuthorView.as_view(), name='author'),
    path('tech/', views.AboutTechView.as_view(), name='tech'),
]
