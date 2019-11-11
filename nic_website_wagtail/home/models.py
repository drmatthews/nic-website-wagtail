from __future__ import absolute_import, unicode_literals

from modelcluster.fields import ParentalKey

from django.conf import settings
from django.db import models
from django.utils.html import format_html

from wagtail.core.models import Page, Orderable
from wagtail.core import blocks
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import (
    FieldPanel, PageChooserPanel,
    StreamFieldPanel, InlinePanel,
    MultiFieldPanel
)
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtailgmaps.edit_handlers import MapFieldPanel

from wagtailmedia.edit_handlers import MediaChooserPanel
from wagtailmedia.blocks import AbstractMediaChooserBlock

from nic_website_wagtail.nicpages.models import BlogPage

GOOGLE_MAPS_KEY = settings.GOOGLE_MAPS_KEY


class HomePageVideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        player_code = '''
        <div>
            <video id="homepage-video" autoplay loop width="320" height="240" controls>
                <source src="{0}" type="video/mp4">
                <source src="{0}" type="video/webm">
                <source src="{0}" type="video/ogg">
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, value.file.url)


class HomePage(Page):

    template = "home/home_page.html"
    max_count = 1

    banner_title = models.CharField(max_length=100, blank=False, null=True)
    banner_subtitle = RichTextField(features=["bold", "italic"])

    map_title = models.CharField(max_length=255, blank=False, null=True)
    street = models.CharField(max_length=255, blank=False, null=True)
    postcode = models.CharField(max_length=255, blank=False, null=True)
    city = models.CharField(max_length=255, blank=False, null=True)
    map_long = models.CharField(max_length=255, blank=False, null=True)
    map_lat = models.CharField(max_length=255, blank=False, null=True)
    map_zoom_level = models.CharField(max_length=3, blank=False, null=True)
    width = models.IntegerField(blank=False, null=True)
    height = models.IntegerField(blank=False, null=True)

    body = StreamField([
        ('heading', blocks.CharBlock(classname="full title", icon='title')),
        ('paragraph', blocks.RichTextBlock(icon='pilcrow')),
        ('media', HomePageVideoBlock(icon='media')),
    ])

    content_panels = Page.content_panels + [
        FieldPanel("banner_title"),
        FieldPanel("banner_subtitle"),
        StreamFieldPanel('body'),
        MultiFieldPanel(
           [
                FieldPanel("map_title"),
                FieldPanel("street"),
                FieldPanel("postcode"),
                FieldPanel("city"),
                FieldPanel("map_long"),
                FieldPanel("map_lat"),
                FieldPanel("map_zoom_level"),
                FieldPanel("width"),
                FieldPanel("height")
            ],
            heading="Google map",
            classname="collapsible collapsed"
        ),
        InlinePanel('gallery_images', label="Gallery images"),
        InlinePanel('systems', label="Systems available"),
        InlinePanel('suppliers', label="Supplier images"),
    ]

    class Meta:
        verbose_name = "Home Page"
        verbose_name_plural = "Home Pages"

    def blogs(self):
        # Get list of live blog pages that are
        # descendants of the ResourceIndexPage page
        blogs = BlogPage.objects.all().order_by('-date')

        return blogs[0:1]

    def get_context(self, request):
        context = super(HomePage, self).get_context(request)
        context['blogs'] = self.blogs()
        context['google_maps_key'] = GOOGLE_MAPS_KEY
        return context


class HomePageGalleryImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='gallery_images')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('caption'),
    ]


class SystemCard(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='systems')
    title = models.CharField(max_length=50, blank=False, null=True)
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )
    caption = models.CharField(blank=True, max_length=250)
    equipment_page = models.ForeignKey(
        "wagtailcore.Page",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
   )    

    panels = [
        FieldPanel("title"),
        ImageChooserPanel('image'),
        PageChooserPanel("equipment_page"),
        FieldPanel('caption'),
    ]


class SupplierImage(Orderable):
    page = ParentalKey(HomePage, on_delete=models.CASCADE, related_name='suppliers')
    image = models.ForeignKey(
        'wagtailimages.Image', on_delete=models.CASCADE, related_name='+'
    )   

    panels = [
        ImageChooserPanel('image'),
    ]