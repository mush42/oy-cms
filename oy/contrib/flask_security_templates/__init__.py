# -*- coding: utf-8 -*-
"""
    oy.contrib.flask_security_templates
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    If you want to override the default security templates,
    you should use this module

"""

from jinja2 import TemplateNotFound
from flask import current_app
from flask.helpers import locked_cached_property
from oy.contrib.extbase import OyExtBase


class FlaskSecurityTemplates(OyExtBase):

    module_args = dict(
        name="oy.contrib.flask_security_templates",
        import_name="oy.contrib.flask_security_templates",
        static_folder="static",
        template_folder="templates",
    )

    @locked_cached_property
    def jinja_loader(self):
        if "oy.contrib.bs4" not in current_app.modules:
            raise TemplateNotFound(
                "oy.contrib.bs4 .BS4 (bootstrap4) module is needed for rendering this template, and it was not registered with the application"
            )
        return super().jinja_loader
