import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'nic_website_wagtail.settings.production'

execfile(os.path.join('/etc/apache2/', 'nic_production_envvars.py'))

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

