from __future__ import unicode_literals

from django.conf import settings
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

GOOGLE_MAPS_KEY = settings.GOOGLE_MAPS_KEY

new_table_options = {
    'colHeaders': True,
    'rowHeaders': False,
    'editor': 'text',
    'stretchH': 'all',
}

class HeadlineBlock(blocks.CharBlock):
    class Meta:
        template = 'nicpages/blocks/headline.html'

class CentreAlignHeadingBlock(blocks.CharBlock):
    class Meta:
        template = 'nicpages/blocks/centre_heading.html'	


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

    def get_context(self, value):
        context = super(GoogleMapBlock, self).get_context(value)
        context['google_maps_key'] = GOOGLE_MAPS_KEY        
        return context

    class Meta:
        template = 'blocks/google_map.html'
        icon = 'cogs'
        label = 'Google Map'

class VideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
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

class ImageResponsiveBlock(blocks.StructBlock):
    image = ImageChooserBlock()

    class Meta:
        template = 'nicpages/blocks/img_responsive.html'
        icon = 'image'

class EquipmentBannerBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=False)
    image = ImageChooserBlock(required=False)
    page = blocks.PageChooserBlock(required=False)
    external_link = blocks.URLBlock(required=False)

    class Meta:
        template = 'nicpages/blocks/equip_banner.html'

class EquipmentBannerRowBlock(blocks.StructBlock):
    first_image = EquipmentBannerBlock()
    second_image = EquipmentBannerBlock()

    class Meta:
        template = 'nicpages/blocks/equip_row.html'
        icon = 'image'

class DocWithPreviewBlock(blocks.StructBlock):
    preview = ImageChooserBlock()
    doc = DocumentChooserBlock()        

    class Meta:
        template = 'blocks/doc_with_preview.html'
        icon = 'doc-full'

class ColOffsetChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('offset-by-one', 'offset-by-one'), ('offset-by-two', 'offset-by-two'),\
        ('offset-by-three', 'offset-by-three'), ('offset-by-four', 'offset-by-four'),
    ))         

class TwoColumnBlock(blocks.StructBlock):

    #col_one_offset = ColOffsetChoiceBlock()
    #col_two_offset = ColOffsetChoiceBlock()

    left_column = blocks.StreamBlock([
            ('heading', blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ('image', ImageChooserBlock()),
            ('embedded_video', EmbedBlock()),
            ('google_map', GoogleMapBlock()),
        ], icon='arrow-left', label='Left column content')
 
    right_column = blocks.StreamBlock([
            ('heading', blocks.CharBlock(classname="full title")),
            ('paragraph', blocks.RichTextBlock()),
            ('image', ImageChooserBlock()),
            ('embedded_video', EmbedBlock()),
            ('google_map', GoogleMapBlock()),
        ], icon='arrow-right', label='Right column content')
 
    class Meta:
        template = 'nicpages/blocks/two_column_block.html'
        icon = 'placeholder'
        label = 'Two Columns'        

# Global Streamfield definition


class PullQuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock("quote title")
    attribution = blocks.CharBlock()

    class Meta:
        icon = "openquote"


class ImageFormatChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('left', 'Wrap left'), ('right', 'Wrap right'), ('mid', 'Mid width'), ('full', 'Full width'),
    ))

class HTMLAlignmentChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('normal', 'Normal'), ('full', 'Full width'),
    ))


class ImageBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    caption = blocks.RichTextBlock()
    alignment = ImageFormatChoiceBlock()


class AlignedHTMLBlock(blocks.StructBlock):
    html = blocks.RawHTMLBlock()
    alignment = HTMLAlignmentChoiceBlock()

    class Meta:
        icon = "code"        

class DemoStreamBlock(blocks.StreamBlock):
    h2 = blocks.CharBlock(icon="title", classname="title")
    h3 = blocks.CharBlock(icon="title", classname="title")
    h4 = blocks.CharBlock(icon="title", classname="title")
    intro = blocks.RichTextBlock(icon="pilcrow")
    paragraph = blocks.RichTextBlock(icon="pilcrow")
    aligned_image = ImageBlock(label="Aligned image", icon="image")
    pullquote = PullQuoteBlock()
    aligned_html = AlignedHTMLBlock(icon="code", label='Raw HTML')
    document = DocumentChooserBlock(icon="doc-full-inverse")        


# A couple of abstract classes that contain commonly used fields

class LinkFields(models.Model):
    link_external = models.URLField("External link", blank=True)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+'
    )
    link_document = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        related_name='+'
    )

    @property
    def link(self):
        if self.link_page:
            return self.link_page.url
        elif self.link_document:
            return self.link_document.url
        else:
            return self.link_external

    panels = [
        FieldPanel('link_external'),
        PageChooserPanel('link_page'),
        DocumentChooserPanel('link_document'),
    ]

    class Meta:
        abstract = True        

# Carousel items

class CarouselItem(LinkFields):
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    embed_url = models.URLField("Embed URL", blank=True)
    caption = models.CharField(max_length=255, blank=True)

    panels = [
        ImageChooserPanel('image'),
        FieldPanel('embed_url'),
        FieldPanel('caption'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True

class NicGalleryBlock(blocks.StreamBlock):
    image = ImageChooserBlock()
    caption = blocks.CharBlock()

    class Meta:
        icon='image'        


# Related links

class RelatedLink(LinkFields):
    title = models.CharField(max_length=255, help_text="Link title")

    panels = [
        FieldPanel('title'),
        MultiFieldPanel(LinkFields.panels, "Link"),
    ]

    class Meta:
        abstract = True                

class NicPage(Page):
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )   

    body = StreamField([
        ('h1', blocks.CharBlock(icon="title")),
        ('h2', blocks.CharBlock(icon="title")),
        ('h3', blocks.CharBlock(icon="title")),
        ('h4', blocks.CharBlock(icon="title")),
        ('h5', blocks.CharBlock(icon="title")),        
        ('headline', HeadlineBlock()),
        ('centre_heading', CentreAlignHeadingBlock()),
        ('paragraph', blocks.RichTextBlock()),
        ('image', ImageChooserBlock()),
        ('image_responsive', ImageResponsiveBlock()),
        ('doc_with_preview', DocWithPreviewBlock()),
        ('home_video', HomePageVideoBlock(icon='media')),
        ('equipment_banner_row', EquipmentBannerRowBlock()),
        ('google_map', GoogleMapBlock()),
        ('two_columns', TwoColumnBlock()),
        ('image_gallery', NicGalleryBlock()),
        ('table', TableBlock(table_options=new_table_options))
    ],null=True,blank=True)

    content_panels = Page.content_panels + [
    	ImageChooserPanel('main_image'),
        StreamFieldPanel('body'),
    ]

class SlideTransitionChoiceBlock(blocks.FieldBlock):
    field = forms.ChoiceField(choices=(
        ('none', 'none'), ('fade', 'fade'), ('slide', 'slide'), ('convex', 'convex'),\
        ('concave','concave'),('zoom','zoom')
    ))        
