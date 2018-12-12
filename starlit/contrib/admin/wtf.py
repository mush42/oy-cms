# -*- coding: utf-8 -*-
"""
    starlit.contrib.admin.wtf
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
        kwargs["class"] += " tinymce"
        return super(TinymceTextAreaWidget, self).__call__(field, **kwargs)


class TinymceTextAreaField(TextAreaField):
    widget = TinymceTextAreaWidget()

    class Meta:
        @staticmethod
        def extra_js(field):
            return [
                url_for("starlit-admin.static", filename="starlit-admin/vendor/tinymce/tinymce.min.js"),
                url_for("starlit-admin.static", filename="starlit-admin/js/tinymce-setup.js")
            ]