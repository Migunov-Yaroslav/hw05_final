import datetime as dt


def year(request):
    """
    Добавить переменную, выводящую текущий год.

    Используется в шаблоне footer.html
    """
    return {
        'year': dt.datetime.now().year,
    }
