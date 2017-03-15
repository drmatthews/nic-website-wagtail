from __future__ import unicode_literals

from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django import forms
from django.utils.html import format_html

from wagtail.wagtailcore import blocks
from wagtail.wagtailcore.models import Page, Orderable
from wagtail.wagtailcore.fields import RichTextField, StreamField
from wagtail.wagtailadmin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.wagtailadmin.edit_handlers import StreamFieldPanel, PageChooserPanel,\
InlinePanel
from wagtail.wagtailimages.blocks import ImageChooserBlock
from wagtail.wagtaildocs.blocks import DocumentChooserBlock
from wagtail.wagtailembeds.blocks import EmbedBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.wagtailimages.edit_handlers import ImageChooserPanel
from wagtail.wagtaildocs.edit_handlers import DocumentChooserPanel
from wagtail.wagtailsearch import index

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

class GoogleMapBlock(blocks.StructBlock):
	title = blocks.CharBlock(required=True,max_length=255)
	street = blocks.CharBlock(required=True,max_length=255)
	postcode = blocks.CharBlock(required=True,max_length=255)
	city = blocks.CharBlock(required=True,max_length=255)
	map_long = blocks.CharBlock(required=True,max_length=255)
	map_lat = blocks.CharBlock(required=True,max_length=255)
	map_zoom_level = blocks.CharBlock(default=14,required=True,max_length=3)
	width = blocks.IntegerBlock(required=True)
	height = blocks.IntegerBlock(required=True)

	class Meta:
		template = 'blocks/google_map.html'
		icon = 'cogs'
		label = 'Google Map'

class VideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value):
        if not value:
            return ''

        player_code = '''
        <div>
            <video width="320" height="240" controls>
                <source src="{0}" type="video/mp4">
                <source src="{0}" type="video/webm">
                <source src="{0}" type="video/ogg">
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, value.file.url)

class SlideImageChooserBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)

    class Meta:
        template = 'slide_deck/blocks/slide_image.html'
        icon = 'doc-full'

class SlideTransitionChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(
        choices=(
        ('none', 'none'),
        ('fade', 'fade'),
        ('slide', 'slide'),
        ('convex', 'convex'),
        ('concave','concave'),
        ('zoom','zoom')
    ))        

class SubSlideBlock(blocks.StreamBlock):
    subslide_image = ImageChooserBlock()
    subslide_content = blocks.RichTextBlock()

    class Meta:
        template = 'slide_deck/blocks/sub_slide.html'    	
        icon='image'

class SlideBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    transition = SlideTransitionChoiceBlock()
    slide_content = blocks.RichTextBlock()
    sub_slide = SubSlideBlock()

    class Meta:
        icon='image'
        template = 'slide_deck/blocks/slide.html'        

class SlideDeckPage(Page):

    deck = StreamField([
        ('slide', SlideBlock())
    ],null=True,blank=True)

    content_panels = Page.content_panels + [
        StreamFieldPanel('deck'),
    ]