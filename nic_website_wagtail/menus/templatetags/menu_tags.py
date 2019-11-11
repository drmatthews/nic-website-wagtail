"""menus/templatetags/menus_tags.py"""
from django import template

from ..models import MainMenu

register = template.Library()


@register.simple_tag()
def get_menu(slug):
    return MainMenu.objects.get(slug=slug)