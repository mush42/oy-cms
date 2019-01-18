# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.formfields
    ~~~~~~~~~~

    Provide various WTForms custom fields.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.contrib.extbase import OyExtBase
from .tinymce import TinymceTextAreaField
from .ckeditor import CkeditorTextAreaField


class OyFormFields(OyExtBase):

    module_args = dict(
        name="oy.contrib.form_fields",
        import_name="oy.contrib.form_fields",
        static_folder="static",
    )
