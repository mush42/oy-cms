from flask import current_app
from werkzeug.local import LocalProxy
from starlit.boot.exts.sqla import db
from starlit.wrappers import StarlitModule
from .models import SettingsProfile


editable_settings = StarlitModule(__name__, 'editable_settings', builtin=True)


class Settings(object):
    def __init__(self, source):
        self.source = source

    def __getattr__(self, key):
        if key in self.source:
            return self.source[key]
        else:
            raise AttributeError("Setting %s does not exists" %key)

    def edit(self, key, value):
        assert key in self.source, "Setting %s does not exists" %key
        self.source[key] = value
        db.session.commit()


def get_active_settings_profile():
    active_settings_profile = SettingsProfile.query.filter(SettingsProfile.is_active==True).one()
    return active_settings_profile

current_settings_profile= LocalProxy(lambda: get_active_settings_profile())
current_settings = LocalProxy(lambda: Settings(get_active_settings_profile().settings))


@editable_settings.app_context_processor
def inject_settings():
    return dict(
        settings_profile=current_settings_profile,
        settings=current_settings
    )
