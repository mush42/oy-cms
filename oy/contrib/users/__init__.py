# -*- coding: utf-8 -*-
"""
    oy.contrib.users
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides user management functionality.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from oy.babel import lazy_gettext
from oy.dynamicform import Field
from oy.contrib.extbase import OyExtBase
from .admin import register_admin
from .models import *


DEFAULT_PROFILE_FIELDS = (
    Field(
        name="first_name",
        type="text",
        label=lazy_gettext("First Name"),
        required=True,
    ),
    Field(
        name="last_name",
        type="text",
        label=lazy_gettext("Last Name"),
        required=True,
    ),
    Field(
        name="bio",
        type="textarea",
        label=lazy_gettext("Biography"),
    ),
    Field(
        name="picture",
        type="file",
        label=lazy_gettext("Profile Picture"),
    )
)


class UserManager(OyExtBase):
    """Extenssion point to the users management feature"""

    module_args = {"name": "oy.contrib.users", "import_name": "oy.contrib.users"}

    def __init__(self, app=None, profile_fields=None, add_default_profile_fields=True, **kwargs):
        self.profile_fields = profile_fields or []
        if add_default_profile_fields:
            self.profile_fields.extend(DEFAULT_PROFILE_FIELDS)
        super().__init__(app, **kwargs)

    def init_app(self, app):
        app.data["profile_fields"] = self.profile_fields
