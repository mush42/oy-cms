from starlit.plugin import StarlitPlugin 
from starlit.babel import lazy_gettext, gettext, ngettext
from .images import Images


class ImagePlugin(StarlitPlugin):
    """Provides integration with a custom build of Flask-Images"""
    identifier = "flask_images"

    def init_app(self, app, *args, **kwargs):
        self.images = Images(app)
