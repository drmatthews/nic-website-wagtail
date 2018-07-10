from __future__ import absolute_import, unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin

from search_nic import views as search_nic_views
from search_wiki import views as search_wiki_views

from wagtail.wagtailadmin import urls as wagtailadmin_urls
from wagtail.wagtailcore import urls as wagtail_urls
from wagtail.wagtaildocs import urls as wagtaildocs_urls

from nicpages.feed import BlogFeed

urlpatterns = [
    url(r'^django-admin/', include(admin.site.urls)),

    url(r'^admin/', include(wagtailadmin_urls)),
    url(r'^documents/', include(wagtaildocs_urls)),

    url(r'^search_nic/$', search_nic_views.search, name='search_nic'),
    url(r'^search_wiki/$', search_wiki_views.search, name='search_wiki'),

    url(r'news-feed/$', BlogFeed(), name='news-feed'),

    url('^sitemap\.xml$', sitemap),

    url(r'', include(wagtail_urls)),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
