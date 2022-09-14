from django import template


"""Регистрация кастомного фильтра во встроенной библиотеке фильтров и тегов."""
register = template.Library()


@register.filter
def addclass(field, css):
    """
    Добавить полю формы аттрибут class.

    Используется в циклах разных шаблонов для добавления полям аттрибута.
    """

    return field.as_widget(attrs={'class': css})
