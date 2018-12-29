# -*- coding: utf-8 -*-
"""
    starlit.contrib.bs4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4, either served
    directly or from a CDN). along with some helper
    jinja macros.
"""
from collections import namedtuple
from flask import url_for
from starlit.babel import lazy_gettext
from starlit.core import current_settings
from starlit.contrib.extbase import StarlitExtBase


class BS4(StarlitExtBase):

    bs4_cdn_css_url = "https://stackpath.bootstrapcdn.com/"\
        "bootstrap/4.1.2/css/bootstrap.min.css"
    bs4_cdn_js_url = "https://stackpath.bootstrapcdn.com/"\
        "bootstrap/4.1.2/js/bootstrap.bundle.min.js"
    jquery_cdn_url = "https://code.jquery.com/jquery-2.2.4.min.js"

    # Holds info about possible urls
    bs4url = namedtuple("bs4_url", "setting_key local_path")

    # Starlit modules parameters
    module_args = dict(
        name = "starlit.contrib.bs4",
        import_name="starlit.contrib.bs4",
        static_folder = "static",
        template_folder = "templates",
        viewable_name = lazy_gettext("Bootstrap 4")
    )

    res_urls = dict(
        jquery=bs4url("jquerycdn", 'starlit/contrib/bs4/js/jquery.min.js'),
        bs4css=bs4url("bs4cdn_css", 'starlit/contrib/bs4/css/bootstrap.min.css'),
        bs4js=bs4url("bs4cdn_js", 'starlit/contrib/bs4/js/bootstrap.min.js'),
    )

    def init_app(self, app):
        app.context_processor(lambda: {'bs4_url_for': self.bs4_url_for})
        self.settings_provider(category="starlit.contrib.bs4")(lambda m: self.provide_bs4_settings())

    def bs4_url_for(self, restype):
        """Get the full url for the resource
            type (css, js, or jquery) based on 
            the current_settings.bs4_use_cdn
        """
        url_info = self.res_urls[restype]
        if current_settings.bs4_use_cdn:
            return getattr(current_settings, url_info.setting_key)
        return url_for(self.name + ".static", filename=url_info.local_path)

    def provide_bs4_settings(self):
        return (
            {
                "name": "bs4_use_cdn",
                "type": "checkbox",
                "label": "Load bootstrap assets from a content delivery network.",
                "default": lambda f: not app.debug,
            },
            {
                "name": "bs4cdn_css",
                "type": "url",
                "label": "Bootstrap CSS CDN URL",
                "default": self.bs4_cdn_css_url,
            },
            {
                "name": "bs4cdn_js",
                "type": "url",
                "label": "Bootstrap javascript CDN URL",
                "default": self.bs4_cdn_js_url,
            },
            {
                "name": "jquerycdn",
                "type": "url",
                "label": "Jquery CDN URL",
                "default": self.jquery_cdn_url,
            },
        )
