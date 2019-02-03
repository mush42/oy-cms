# -*- coding: utf-8 -*-
"""
    oy.contrib.form_fields.tags_input
    ~~~~~~~~~~

    Provide a WTForms field for entering tags. 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from jinja2 import Markup
from flask import url_for
from wtforms.widgets import TextInput
from wtforms.fields import StringField


class TagsInput(TextInput):
    def __call__(self, field, **kwargs):
        if kwargs.get("class"):
            kwargs["class"] += " tags_input"
        else:
            kwargs.setdefault("class", "tags_input")
        return super().__call__(field, **kwargs)


class TagsField(StringField):
    widget = TagsInput()

    def _value(self):
        if self.data:
            return ",".join(self.data)
        else:
            return ""

    def process_formdata(self, valuelist):
        if valuelist:
            self.data = sorted({tag.strip() for tag in valuelist[0].split(",")})
        else:
            self.data = {}

    def get_field_css(self):
        return [
            url_for(
                "oy-admin-resource-module.static",
                filename="vendor/tags_input/jquery.tagsinput.min.css",
            )
        ]

    def get_field_js(self):
        return [
            url_for(
                "oy-admin-resource-module.static",
                filename="vendor/tags_input/jquery.tagsinput.min.js",
            ),
            Markup(
                '<script type="text/javascript">$(".tags_input").tagsInput()</script>'
            ),
        ]
