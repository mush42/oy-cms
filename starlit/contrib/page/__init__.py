# -*- coding: utf-8 -*-
"""
    starlit.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides default page templates
    as well as fixtures.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from starlit.babel import lazy_gettext
from starlit.contrib.extbase import StarlitExtBase


class Page(StarlitExtBase):

    module_args = dict(
        name = "starlit.contrib.page",
        import_name = "starlit.contrib.page",
        template_folder = "templates",
        viewable_name = lazy_gettext("Page")
    )

    def init_app(self, app):
        app.template_filter(name="unique_string")(lambda s: s)
