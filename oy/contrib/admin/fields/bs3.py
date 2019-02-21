# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.bs3_file_input
    ~~~~~~~~~~

    Provides a custom WTForms field for file input.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from wtforms.widgets import FileInput
from wtforms.fields.simple import FileField
from flask import current_app, url_for


class BootstrapFileInputWidget(FileInput):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        kwargs.setdefault("type", self.input_type)
        kwargs["value"] = False
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        return current_app.jinja_env.get_template(
            "admin/oy/fields/bs4_file_input.html"
        ).render(kwargs=kwargs)


class BootstrapFileInputField(FileField):
    widget = BootstrapFileInputWidget()

    def get_field_js(self):
        return [url_for("oy-admin-resource-module.static", filename="js/fields/file_input.min.js")]
