from __future__ import absolute_import, unicode_literals

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass

WAGTAILEMBEDS_FINDERS = [
    {
        'class': 'nic_website_wagtail.embeds.omero_embed.OmeroFinder',
        # Any other options will be passed as kwargs to the __init__ method
    }
]