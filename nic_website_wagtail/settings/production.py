from __future__ import absolute_import, unicode_literals

from .base import *

DEBUG = False

try:
    from .local import *
except ImportError:
    pass

INSTALLED_APPS += ['mod_wsgi.server', ]

