# -*- coding: utf-8 -*-
"""
    starlit.contrib.page
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides default page templates
    as well as fixtures.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext

page = StarlitModule(
    name="starlit.contrib.page",
    import_name="starlit.contrib.page",
    template_folder="templates",
    viewable_name=lazy_gettext("Page"),
)


@page.app_template_filter()
def unique_string(s):
    return s
