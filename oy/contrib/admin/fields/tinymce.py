# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.wtf
    ~~~~~~~~~~

    Provide WTForms custom fields.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from flask import url_for
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField


class TinymceTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " tinymce"
        else:
            kwargs.setdefault("class", "tinymce")
        return super().__call__(field, **kwargs)


class TinymceTextAreaField(TextAreaField):
    widget = TinymceTextAreaWidget()

    def get_field_js(self):
        return [
            url_for(
                "oy-admin-resource-module.static",
                filename="vendor/tinymce/tinymce.min.js",
            ),
            url_for("oy-admin-resource-module.static", filename="js/tinymce-setup.js"),
        ]
