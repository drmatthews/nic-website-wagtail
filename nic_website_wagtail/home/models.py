from __future__ import absolute_import, unicode_literals

from django.db import models
from django.utils.html import format_html

from wagtail.core import blocks
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import StreamFieldPanel
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.core.models import Page

from nic_website_wagtail.nicpages.models import BlogPage


class HomePageVideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        player_code = '''
        <div>
            <video id="video" autoplay loop width="320" height="240" controls>
                <source src="{0}" type="video/mp4">
                <source src="{0}" type="video/webm">
                <source src="{0}" type="video/ogg">
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, value.file.url)


class HomePageStreamBlock(blocks.StreamBlock):
    paragraph = blocks.RichTextBlock()
    home_video = HomePageVideoBlock(icon='media')


class HomePage(Page):
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    body = StreamField(
        HomePageStreamBlock(),
        null=True,
        blank=True
    )

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        StreamFieldPanel('body'),
    ]

    def blogs(self):
        # Get list of live blog pages that are
        # descendants of the ResourceIndexPage page
        blogs = BlogPage.objects.all().order_by('-date')

        return blogs[0:1]

    def get_context(self, request):
        context = super(HomePage, self).get_context(request)
        context['blogs'] = self.blogs()
        return context
