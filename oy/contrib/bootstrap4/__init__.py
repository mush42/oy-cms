# -*- coding: utf-8 -*-
"""
    oy.contrib.bootstrap4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4, either served
    directly or from a CDN). along with some helper
    jinja macros.
"""

from collections import namedtuple
from flask import current_app, url_for
from oy.babel import lazy_gettext
from oy.core import current_settings
from oy.contrib.extbase import OyExtBase


class Bootstrap4(OyExtBase):

    # Holds info about possible urls
    bs4url = namedtuple("bs4_url", "setting_key local_path")

    # Oy modules parameters
    module_args = dict(
        name="oy.contrib.bootstrap4",
        import_name="oy.contrib.bootstrap4",
        static_folder="static",
        template_folder="templates",
        viewable_name=lazy_gettext("Bootstrap 4"),
    )

    res_urls = dict(
        jquery=bs4url("jquerycdn", "js/jquery.min.js"),
        bs4css=bs4url("bs4cdn_css", "css/"),
        bs4js=bs4url("bs4cdn_js", "js/bootstrap.min.js"),
    )

    def init_app(self, app):
        app.config["BS4_SKIN"] = "default"
        app.context_processor(lambda: {"bs4_url_for": self.bs4_url_for})
        self.settings_provider(category="oy.contrib.bootstrap4")(
            lambda m: self.provide_bs4_settings()
        )

    def bs4_url_for(self, restype):
        """Get the full url for the resource
            type (css, js, or jquery) based on 
            the current_settings
        """
        url_info = self.res_urls[restype]
        url = getattr(current_settings, url_info.setting_key, None)
        if url is not None:
            return url
        elif restype == "bs4css":
            css = current_app.config["BS4_SKIN"]
            if css == "default":
                suffix = "bootstrap.min.css"
            else:
                suffix = f"swatch/{css}.css"
            return url_for(
                self.name + ".static", filename=url_info.local_path + f"{suffix}"
            )
        return url_for(self.name + ".static", filename=url_info.local_path)

    def provide_bs4_settings(self):
        return (
            {"name": "bs4cdn_css", "type": "url", "label": "Bootstrap CSS CDN URL"},
            {
                "name": "bs4cdn_js",
                "type": "url",
                "label": "Bootstrap javascript CDN URL",
            },
            {"name": "jquerycdn", "type": "url", "label": "Jquery CDN URL"},
        )
