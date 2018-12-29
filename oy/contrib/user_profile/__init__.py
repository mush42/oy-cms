from oy.babel import lazy_gettext
from oy.contrib.extbase import OyExtBase
from .admin import register_admin
from .models import register_user_profiles_event_listener


class UserProfile(OyExtBase):
    """Extenssion point to the user profile feature"""

    module_args = dict(
        name="oy.contrib.userprofile", import_name="oy.contrib.userprofile"
    )

    def __init__(self, app=None, profile_fields=None, **kwargs):
        self.profile_fields = profile_fields
        super().__init__(app, **kwargs)

    def init_app(self, app):
        app.data["profile_fields"] = self.profile_fields or {}
        with app.app_context():
            register_user_profiles_event_listener()
