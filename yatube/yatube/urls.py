from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

"""
Список URL проекта:
-/ - основные страницы;
- auth/ - страницы управления пользователями (регистрация, вход/выход и пр.);
- about/ - страницы с информацией об авторе и используемых технологиях.
"""
urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('about/', include('about.urls', namespace='about')),
    path('__debug__/', include('debug_toolbar.urls')),
]

handler404 = 'core.views.page_not_found'
handler403 = 'core.views.permission_denied'
handler500 = 'core.views.server_error'

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
    )

    # import debug_toolbar
    # urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
