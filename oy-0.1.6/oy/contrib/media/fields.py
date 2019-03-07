# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.media_selector
    ~~~~~~~~~~

    Provide WTForms custom fields.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from jinja2 import Markup
from wtforms.widgets import HiddenInput
from wtforms.fields import StringField
from flask import current_app, url_for


class MediaSelectorWidget(HiddenInput):

    template_name = "admin/oy/fields/media_selector_field.html"

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("type", self.input_type)
        if "value" not in kwargs:
            kwargs["value"] = field._value()
        if "required" not in kwargs and "required" in getattr(field, "flags", []):
            kwargs["required"] = True
        input = Markup(f"<input {self.html_params(name=field.name, **kwargs)} />")
        template = current_app.jinja_env.get_template(self.template_name)
        return template.render(html_hidden_input=input, field=field, kwargs=kwargs)


class MediaSelectorField(StringField):
    widget = MediaSelectorWidget()

    def __init__(self, model, **kwargs):
        super().__init__(**kwargs)
        self.model = model

    def get_image(self, id):
        obj = self.model.query.filter_by(id=id).one_or_none()
        if obj is not None:
            return dict(
                url=url_for("image_admin.internal_serve", file_id=obj.file_id),
                thum_url=url_for(
                    "image_admin.internal_serve", file_id=obj.file_id, size="xs"
                ),
                title=obj.title,
            )

    def get_field_js(self):
        return [
            url_for("oy.contrib.media.admin.static", filename="js/media-admin.min.js")
        ]
