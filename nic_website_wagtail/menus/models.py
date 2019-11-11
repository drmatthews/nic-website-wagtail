"""menus/models.py"""
from django.db import models

from django_extensions.db.fields import AutoSlugField
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.edit_handlers import (
    MultiFieldPanel,
    InlinePanel,
    FieldPanel,
    PageChooserPanel,
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.snippets.edit_handlers import SnippetChooserPanel
from wagtail.core.models import Orderable
from wagtail.snippets.models import register_snippet



class MenuItem(Orderable):
    """Class representing items in a menu."""
    link_title = models.CharField(
        blank=True,
        null=True,
        max_length=50
    )
    link_url = models.CharField(
        max_length=500,
        blank=True
    )
    link_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        related_name="+",
        on_delete=models.CASCADE,
    )
    link_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    open_in_new_tab = models.BooleanField(default=False, blank=True)

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_url:
            return self.link_url
        return '#'

    @property
    def title(self):
        if self.link_page and not self.link_title:
            return self.link_page.title
        elif self.link_title:
            return self.link_title
        return 'Missing Title'



class SubMenuItem(MenuItem):
    """Class representing items in a sub-menu."""
    page = ParentalKey("SubMenu", related_name="sub_menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        ImageChooserPanel('link_image'),
        FieldPanel("open_in_new_tab"),
    ]


class MainMenuItem(MenuItem):
    """Class representing items in a main-menu."""
    submenu = models.ForeignKey(
        'SubMenu',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )    

    page = ParentalKey("MainMenu", related_name="main_menu_items")

    panels = [
        FieldPanel("link_title"),
        FieldPanel("link_url"),
        PageChooserPanel("link_page"),
        ImageChooserPanel('link_image'),
        SnippetChooserPanel('submenu'),
        FieldPanel("open_in_new_tab"),
    ]


class Menu(ClusterableModel):
    """The main menu clusterable model."""

    title = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="title", editable=True)
    # slug = models.SlugField()

    def __str__(self):
        return self.title


@register_snippet
class MainMenu(Menu):
    """Class representing a main menu - this is a menu that
    can contain a sub-menu.
    """
    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Main Menu"),
        InlinePanel("main_menu_items", label="Menu Item")
    ]


@register_snippet
class SubMenu(Menu):
    """Class representing a sub-menu - cannot contain another
    sub-menu."""
    panels = [
        MultiFieldPanel([
            FieldPanel("title"),
            FieldPanel("slug"),
        ], heading="Sub Menu"),
        InlinePanel("sub_menu_items", label="Menu Item")
    ]