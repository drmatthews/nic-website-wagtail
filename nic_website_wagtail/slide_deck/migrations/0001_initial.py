# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-25 10:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import nic_website_wagtail.slide_deck.models
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('wagtailcore', '0032_add_bulk_delete_page_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlideDeckPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
                ('deck', wagtail.core.fields.StreamField([('slide', wagtail.core.blocks.StructBlock([(b'image', wagtail.images.blocks.ImageChooserBlock(required=False)), (b'transition', nic_website_wagtail.slide_deck.models.SlideTransitionChoiceBlock()), (b'slide_content', wagtail.core.blocks.RichTextBlock()), (b'sub_slide', wagtail.core.blocks.StreamBlock([(b'subslide_image', wagtail.images.blocks.ImageChooserBlock()), (b'subslide_content', wagtail.core.blocks.RichTextBlock())]))]))], blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
    ]