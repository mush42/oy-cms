from starlit.wrappers import StarlitModule
from starlit.babel import lazy_gettext
from .admin import register_admin
from .models import register_user_profiles_event_listener


class UserProfile(StarlitModule):
    """Extenssion point to the user profile feature"""

    def __init__(self, app=None):
        super().__init__("starlit.contrib.user_profile", __name__)
        if app:
            self.init_app(app)

    def init_app(self, app):
        with app.app_context():
            register_user_profiles_event_listener()
        app.register_module(self)
