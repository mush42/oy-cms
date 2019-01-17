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


class CkeditorTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " ckeditor"
        else:
            kwargs.setdefault("class", "ckeditor")
        return super().__call__(field, **kwargs)


class CkeditorTextAreaField(TextAreaField):
    widget = CkeditorTextAreaWidget()

    class Meta:
        @staticmethod
        def extra_js(field):
            return [
                url_for(
                    "oy.contrib.formfields.static",
                    filename="ckeditor/ckeditor.js",
                ),
                url_for(
                    "oy.contrib.formfields.static",
                    filename="js/ckeditor-setup.js",
                ),
            ]
