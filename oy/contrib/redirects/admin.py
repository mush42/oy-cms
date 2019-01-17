# -*- coding: utf-8 -*-
"""
    oy.contrib.redirects.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the admin interface for editing oy redirects.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.models import db
from oy.babel import lazy_gettext
from oy.contrib.admin.wrappers import OyModelView
from .models import Redirect


class RedirectsAdmin(OyModelView):
    form_columns = ("from_url", "to_url", "to_page", "permanent")
    column_list = ("from_url", "to_url", "permanent")
    column_editable_list = ("from_url", "to_url")


def register_admin(app, admin):
    admin.add_view(
        RedirectsAdmin(
            Redirect,
            db.session,
            name=lazy_gettext("Redirects"),
            menu_icon_type="fa",
            menu_icon_value="fa-refresh",
        )
    )
