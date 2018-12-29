# -*- coding: utf-8 -*-
"""
    starlit.contrib.flask_security_templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    If you want to override the default security templates,
    you should use this module

"""

from jinja2 import TemplateNotFound
from flask import current_app
from flask.helpers import locked_cached_property
from starlit.contrib.extbase import StarlitExtBase


class FlaskSecurityTemplates(StarlitExtBase):

    module_args = dict(
        name = "starlit.contrib.flask_security_templates",
        import_name = "starlit.contrib.flask_security_templates",
        static_folder = "static",
        template_folder = "templates"
    )

    @locked_cached_property
    def jinja_loader(self):
        if 'starlit.contrib.bs4' not in current_app.modules:
            raise TemplateNotFound("starlit.contrib.bs4 .BS4 (bootstrap4) module is needed for rendering this template, and it was not registered with the application")
        return super().jinja_loader
