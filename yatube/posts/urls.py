from django.urls import path

from . import views

app_name = 'posts'

"""
Список URL приложения posts:
- / - главная страница сервиса;
- group/<slug:slug>/ - страница сообщества;
- profile/<str:username>/ - страница пользователя;
- posts/<int:post_id>/ - страница просмотра поста;
- create/ - страница создания поста;
- posts/<int:post_id>/edit/ - страница редактирования поста;
"""
urlpatterns = [
    path('', views.index, name='index'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('create/', views.post_create, name='post_create'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    path(
        'posts/<int:post_id>/comment/',
        views.add_comment,
        name='add_comment',
    ),
    path('follow/', views.follow_index, name='follow_index'),
    path(
        'profile/<str:username>/follow/',
        views.profile_follow,
        name='profile_follow',
    ),
    path(
        'profile/<str:username>/unfollow/',
        views.profile_unfollow,
        name='profile_unfollow'
    ),
]
