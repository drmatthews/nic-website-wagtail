from __future__ import unicode_literals

from django.conf import settings
from django import forms
from django.db import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse
from django import forms
from django.utils.html import format_html
from django.utils.encoding import force_text
from django.utils.safestring import mark_safe

from wagtail.core import blocks
from wagtail.embeds.blocks import EmbedBlock, EmbedValue
from wagtail.embeds.format import embed_to_frontend_html
from wagtail.core.models import Page, Orderable
from wagtail.core.fields import RichTextField, StreamField
from wagtail.admin.edit_handlers import FieldPanel, MultiFieldPanel
from wagtail.admin.edit_handlers import StreamFieldPanel, PageChooserPanel,\
InlinePanel
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtailmedia.blocks import AbstractMediaChooserBlock
from wagtail.contrib.table_block.blocks import TableBlock
from wagtail.images.edit_handlers import ImageChooserPanel
from wagtail.documents.edit_handlers import DocumentChooserPanel
from wagtail.search import index
from wagtailmenus.models import MenuPage

from taggit.models import TaggedItemBase

from modelcluster.fields import ParentalKey
from modelcluster.tags import ClusterTaggableManager

from pygments import highlight
from pygments.formatters import get_formatter_by_name
from pygments.lexers import get_lexer_by_name

GOOGLE_MAPS_KEY = settings.GOOGLE_MAPS_KEY


class VideoBlock(AbstractMediaChooserBlock):
    def render_basic(self, value, context=None):
        if not value:
            return ''

        player_code = '''
        <div>
            <video autoplay loop width="600" height="450" controls>
                <source src="{0}" type="video/mp4">
                <source src="{0}" type="video/webm">
                <source src="{0}" type="video/ogg">
                Your browser does not support the video tag.
            </video>
        </div>
        '''

        return format_html(player_code, value.file.url)


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

    def get_searchable_content(self, value):
        return [force_text(value)]

    class Meta:
        template = 'wiki/blocks/doc_with_preview.html'
        icon = 'doc-full'


class DocWithPreviewRowBlock(blocks.StructBlock):
    first_doc = DocWithPreviewBlock()
    second_doc = DocWithPreviewBlock()

    def get_searchable_content(self, value):
        return [force_text(value)]

    class Meta:
        template = 'wiki/blocks/doc_with_preview_row.html'
        icon = 'doc-full'


class OmeroEmbedValue(EmbedValue):
    """
    Override the native EmbedBlock value to contruct the
    OMERO url from the image ID (in OMERO).
    """
    def __init__(self, image_id, omero_type):
        # print("image_id in embedvalue: {}".format(str(image_id)))
        self.image_id = image_id
        self.omero_type = omero_type
        self.url = ''
        if 'image' in omero_type:
            self.url = "image/{0}".format(str(image_id))
        else:
            self.url = "thumbnail/{0}".format(str(image_id))
        # print("self.url: {}".format(self.url))


class OmeroEmbedBlock(blocks.IntegerBlock):
    def __init__(self, omero_type='image', **kwargs):
        super().__init__(**kwargs)

        self.omero_type = omero_type

    def get_default(self):
        # Allow specifying the default for an OmeroEmbedBlock as either an
        # OmeroEmbedValue or None.
        # print("default in get default: {}".format(self.meta.default))
        if not self.meta.default:
            return None
        elif isinstance(self.meta.default, OmeroEmbedValue):
            return self.meta.default
        else:
            # assume default has been passed as a string
            return OmeroEmbedValue(self.meta.default, self.omero_type)

    def to_python(self, value):
        # The JSON representation of an OmeroEmbedBlock's value is an integer;
        # this should be converted to an OmeroEmbedValue (or None).
        # print("value in to_python: {}".format(value))
        if not value:
            return None
        else:
            return OmeroEmbedValue(value, self.omero_type)

    def get_prep_value(self, value):
        # serialisable value should be an integer
        # print("prep value: {}".format(type(value)))
        if value is None:
            return ''
        else:
            return int(value.url[-1])

    def value_for_form(self, value):
        # the value to be handled by the IntegerField is a
        # integer (greater than 0) or None
        # print("value for form: {}".format(value))
        if value is None:
            return None
        else:
            return int(value.url[-1])

    def value_from_form(self, value):
        # convert the value returned from the form
        # (an integer [image_id]) to an OmeroEmbedValue (or None)
        # print("value from form: {}".format(value))
        if not value:
            return None
        else:
            return OmeroEmbedValue(value, self.omero_type)


class OmeroImageListBlock(blocks.ListBlock):
    class Meta:
        template = 'wiki/blocks/omero_image_gallery.html'
        icon = 'image'


class OmeroDatasetBlock(blocks.StructBlock):
    MICROSCOPE_CHOICES = (
        ('a1_inv_confocal', 'A1 Inverted Confocal'),
        ('a1_up_confocal', 'A1 Upright Confocal'),
        ('a1r_confocal', 'A1R Confocal'),
        ('a1r_mp', 'A1R Multi-photon'),
    )

    microscope = blocks.ChoiceBlock(choices=MICROSCOPE_CHOICES)
    thumbnail = OmeroEmbedBlock(omero_type='thumbnail')
    gallery = blocks.PageChooserBlock()

    class Meta:
        template = 'wiki/blocks/omero_dataset_gallery.html'
        icon = 'image'


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
        ('video', VideoBlock(icon='media')),
        ('OMERO_Dataset', OmeroDatasetBlock()),
        (
            'OMERO_Gallery', OmeroImageListBlock(
                OmeroEmbedBlock(label="Image ID")
            )
        ),
    ], null=True, blank=True)

    content_panels = Page.content_panels + [
        ImageChooserPanel('main_image'),
        StreamFieldPanel('body'),
    ]

    search_fields = Page.search_fields + [  # Inherit search_fields from Page
        index.SearchField('body'),
    ]

    def get_context(self, request):
        context = super(WikiPage, self).get_context(request)

        # Add extra variables and return the updated context
        context['google_maps_key'] = GOOGLE_MAPS_KEY
        return context
