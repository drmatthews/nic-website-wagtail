from wagtail.embeds.finders.base import EmbedFinder


class OmeroFinder(EmbedFinder):
    def __init__(self, **options):
        pass

    def accept(self, url):
        """
        Returns True if this finder knows how to fetch an embed for the URL.

        This should not have any side effects (no requests to external servers)
        """
        return True

    def find_embed(self, url, max_width=None):
        """
        Takes a URL and max width and returns a dictionary of information
        about the content to be used for embedding it on the site.

        This is the part that may make requests to external APIs.
        """
        img_id = url[url.find('/') + 1:]
        if 'image' in url:
            img_anchor = (
                '<a href="http://localhost:4080/public_iviewer/'
                '?images={0}/">'.format(img_id)
            )
            thumb_anchor = (
                '<img class="img-thumbnail" '
                'src="http://localhost:4080/webgateway/'
                'render_thumbnail/{0}/200/200"/></a>'.format(img_id)
            )
            metadata_anchor = (
                '<p>'
                '<a href="http://localhost:4080/gallery/imgData/{0}/'
                'Camera.Size T" onclick="load_info(event,this);" '
                'data-id="{0}">Image info</a>'
                '</p>'.format(img_id)
            )
            html = img_anchor + thumb_anchor + metadata_anchor
        elif 'thumbnail' in url:
            thumb_anchor = (
                '<img class="img-thumbnail" '
                'src="http://localhost:4080/webgateway/'
                'render_thumbnail/{0}/200/200"/>'.format(img_id)
            )
            html = thumb_anchor
        return {
            'title': "Omero test",
            'author_name': "Dan",
            'provider_name': "OMERO server",
            'type': "photo",
            'width': 200,
            'height': 200,
            'html': html
        }
