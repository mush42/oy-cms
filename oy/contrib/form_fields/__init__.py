# -*- coding: utf-8 -*-
"""
    oy.contrib.formfields
    ~~~~~~~~~~

    Provide various WTForms custom fields.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from wtforms.form import BaseForm
from jinja2 import contextfunction
from oy.contrib.extbase import OyExtBase
from .tinymce import TinymceTextAreaField
from .ckeditor import CkeditorTextAreaField


class OyFormFields(OyExtBase):

    module_args = dict(
        name="oy.contrib.form_fields",
        import_name="oy.contrib.form_fields",
        static_folder="static",
    )

    def init_app(self, app):
        app.context_processor(lambda: {
            "get_form_css": self.get_form_static("css"),
            "get_form_js": self.get_form_static("js")
        })

    def _get_static_for_field(self, field, type_):
        files = getattr(field, f"get_field_{type_}", [])
        if callable(files):
            files = files()
        return files

    def get_form_static(self, type_):
        @contextfunction
        def form_static_getter(context):
            rv = []
            for form in (v for v in context.values() if isinstance(v, BaseForm)):
                for field in form:
                    for file in (fi for fi in self._get_static_for_field(field, type_) if fi not in rv):
                        rv.append(file)
            return rv
        return form_static_getter
