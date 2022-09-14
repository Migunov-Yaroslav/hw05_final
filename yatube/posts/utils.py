from django.core.paginator import Paginator

from .constants import POSTS_ON_PAGE


def paginator_func(request, posts):
    """
    Создать паджинатор.

    Используется для постраничного вывода постов в шаблонах:
    - index.html;
    - group_list.html;
    - profile.html;
    """
    paginator = Paginator(posts, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return page_obj
