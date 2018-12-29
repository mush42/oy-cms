# -*- coding: utf-8 -*-
"""
    oy.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides default page templates
    as well as fixtures.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.babel import lazy_gettext
from oy.contrib.extbase import OyExtBase


class Page(OyExtBase):

    module_args = dict(
        name="oy.contrib.page",
        import_name="oy.contrib.page",
        template_folder="templates",
        viewable_name=lazy_gettext("Page"),
    )

    def init_app(self, app):
        app.template_filter(name="unique_string")(lambda s: s)
