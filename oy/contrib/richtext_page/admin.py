# -*- coding: utf-8 -*-
"""
    oy.contrib.richtext_page.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the admin interface for editing oy rich text pages.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.models import db
from oy.babel import lazy_gettext
from oy.contrib.admin.core.page import PageAdmin
from oy.contrib.formfields import TinymceTextAreaField
from .models import RichTextPage


class RichTextPageAdmin(PageAdmin):

    form_columns = list(PageAdmin.form_columns)
    form_columns.insert(4, "content")
    form_overrides = {"content": TinymceTextAreaField}


def register_admin(app, admin):
    admin.add_view(
        RichTextPageAdmin(
            RichTextPage,
            db.session,
            name=lazy_gettext("Rich Text Pages"),
            menu_icon_type="fa",
            menu_icon_value="fa-newspaper-o",
        )
    )
