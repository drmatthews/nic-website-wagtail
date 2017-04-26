from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django import forms
from django.utils.html import format_html
from django.utils.safestring import mark_safe

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
from wagtailmenus.models import MenuPage

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

GOOGLE_MAPS_KEY = settings.GOOGLE_MAPS_KEY

class CodeBlock(blocks.StructBlock):
    """
    Code Highlighting Block
    """
    LANGUAGE_CHOICES = (
        ('python', 'Python'),
        ('java', 'Java'),
        ('imagej', 'ImageJ Macro'),
        ('bash', 'Bash/Shell'),
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('scss', 'SCSS'),
    )

    language = blocks.ChoiceBlock(choices=LANGUAGE_CHOICES)
    code = blocks.TextBlock()

    class Meta:
        icon = 'code'

    def render(self, value, context=None):
        src = value['code'].strip('\n')
        lang = value['language']
        if 'imagej' in lang:
            lang = 'java'

        lexer = get_lexer_by_name(lang)

        formatter = get_formatter_by_name(
            'html',
            linenos=None,
            cssclass='highlight',
            style='colorful',
            noclasses=False,
        )

        return mark_safe(highlight(src, lexer, formatter))

class DocWithPreviewBlock(blocks.StructBlock):
    preview = ImageChooserBlock()
    doc = DocumentChooserBlock()        

    class Meta:
        template = 'wiki/blocks/doc_with_preview.html'
        icon = 'doc-full'

class DocWithPreviewRowBlock(blocks.StructBlock):
    first_doc = DocWithPreviewBlock()
    second_doc = DocWithPreviewBlock()

    class Meta:
        template = 'wiki/blocks/doc_with_preview_row.html'
        icon = 'doc-full'        

class WikiPage(MenuPage):
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )   

    body = StreamField([
        ('paragraph', blocks.RichTextBlock()),
        ('doc_with_preview', DocWithPreviewBlock()),
        ('doc_with_preview_row', DocWithPreviewRowBlock()),
        ('code', CodeBlock()),
    ],null=True,blank=True)

    content_panels = Page.content_panels + [
    	ImageChooserPanel('main_image'),
        StreamFieldPanel('body'),
    ]

    search_fields = Page.search_fields + [ # Inherit search_fields from Page
        index.SearchField('body'),
    ]     

    def get_context(self, request):
        context = super(WikiPage, self).get_context(request)

        # Add extra variables and return the updated context
        context['google_maps_key'] = GOOGLE_MAPS_KEY
        return context    	
