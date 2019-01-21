# -*- coding: utf-8 -*-
"""
    oy.contrib.media.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the admin interface for adding and removing images and documents.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask_admin import BaseView, expose
from flask_wtf import Form
from oy.models import db
from oy.babel import lazy_gettext
from oy.contrib.admin.wrappers import AuthenticationViewMixin
from oy.dynamicform import DynamicForm
from .models import Image, Document


class GenericMediaAdmin(BaseView, AuthenticationViewMixin):

    @expose("/")
    def index(self):
        return self.render("oy/contrib/media/admin/index.html")

    def get_form(self, obj=None):
        return DynamicForm(fieldset=(
            {
                "name": "title",
                "label": "Title",
                "type": "text"
            },
            {
                "name": "file",
                "label": "File",
                "type": "file"
            },
        )).form


def register_admin(app, admin):
    admin.add_view(
        GenericMediaAdmin(
            name=lazy_gettext("Images"),
            endpoint="images",
            url="media/images/",
            menu_icon_type="fa",
            menu_icon_value="fa-photo",
            menu_order=500
        )
    )
    admin.add_view(
        GenericMediaAdmin(
            name=lazy_gettext("Documents"),
            endpoint="documents",
            url="media/documents/",
            menu_icon_type="fa",
            menu_icon_value="fa-file",
            menu_order=400
        )
    )
