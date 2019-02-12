from oy.babel import lazy_gettext
from oy.contrib.extbase import OyExtBase
from .admin import register_admin
from .models import *


class UserManager(OyExtBase):
    """Extenssion point to the users management feature"""

    module_args = dict(name="oy.contrib.users", import_name="oy.contrib.users")

    def __init__(self, app=None, profile_fields=None, **kwargs):
        self.profile_fields = profile_fields
        super().__init__(app, **kwargs)

    def init_app(self, app):
        app.data["profile_fields"] = self.profile_fields or {}
