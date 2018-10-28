# -*- coding: utf-8 -*-
"""
    starlit.contrib.admin.wtf
    ~~~~~~~~~~

    Provide WTForms custom fields.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from wtforms.widgets import TextArea
from wtforms.fields import TextAreaField


class TinymceTextAreaWidget(TextArea):
    def __call__(self, field, **kwargs):
        kwargs.setdefault("class_", "tinymce")
        return super(TinymceTextAreaWidget, self).__call__(field, **kwargs)


class TinymceTextAreaField(TextAreaField):
    widget = TinymceTextAreaWidget()
