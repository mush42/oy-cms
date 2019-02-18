# -*- coding: utf-8 -*-
"""
    oy.contrib.bootstrap4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4, along with some helper
    jinja macros.
"""

from flask import current_app, url_for
from oy.contrib.extbase import OyExtBase


class Bootstrap4(OyExtBase):

    # Oy modules parameters
    module_args = dict(
        name="oy.contrib.bootstrap4",
        import_name="oy.contrib.bootstrap4",
        static_folder="static",
        template_folder="templates",
    )

    file_paths = dict(
        jquery="vendor/jquery/jquery.min.js",
        bs4css="vendor/bootstrap/css/bootstrap.min.css",
        bs4js="vendor/bootstrap/js/bootstrap.min.js"
    )

    def init_app(self, app):
        app.context_processor(lambda: {"bs4_url_for": self.bs4_url_for})

    def bs4_url_for(self, restype):
        """Get the full url for the resource
            type (css, js, or jquery).
        """
        if restype == "bs4css":
            swatch = current_app.config.get("BS4_SKIN")
            if swatch is None:
                filename = self.file_paths["bs4css"]
            else:
                filename = "vendor/swatch/{swatch}/bootstrap.min.css"
            return url_for(
                self.name + ".static", filename=filename
            )
        return url_for(self.name + ".static", filename=self.file_paths[restype])
