from starlit.babel import lazy_gettext
from starlit.contrib.extbase import StarlitExtBase
from .admin import register_admin
from .models import register_user_profiles_event_listener


class UserProfile(StarlitExtBase):
    """Extenssion point to the user profile feature"""

    module_args = dict(
        name="starlit.contrib.userprofile",
        import_name="starlit.contrib.userprofile"
    )
    def __init__(self, app=None, profile_fields=None, **kwargs):
        self.profile_fields = profile_fields
        super().__init__(app, **kwargs)

    def init_app(self, app):
        app.data['profile_fields'] = self.profile_fields or {}
        with app.app_context():
            register_user_profiles_event_listener()
