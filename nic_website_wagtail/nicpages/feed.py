from django.db import models
from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from .models import BlogPage


class BlogFeed(Feed):
    title = "Nikon Imaging Centre news articles"
    link = "/news-feed/"
    description = "Nikon Imaging Centre @ King's news as it is published"

    def items(self):
        return BlogPage.objects.live().order_by('-date')

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.intro
