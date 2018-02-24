from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.local import LocalProxy
from flask import current_app
from starlit.exceptions import StarlitException
from starlit.boot.exts.sqla import db
from starlit.wrappers import StarlitModule
from .models import SettingsProfile


editable_settings = StarlitModule('editable_settings', __name__, builtin=True)


class SettingDoesNotExist(StarlitException):
    """Raised when accessing a setting that does
    not exist in the database nor the current_app settings
    """


class Settings(object):
    def __init__(self, source):
        self.source = source

    def __getattr__(self, key):
        if key in self.source:
            return self.source[key]
        elif key in current_app._provided_settings:
            val = current_app._provided_settings[key].default
            self.edit(key, val)
            return val
        else:
            raise SettingDoesNotExist("Setting %s does not exists" %key)

    def edit(self, key, value):
        if key not in chain(self.source, current_app._provided_settings):
            raise SettingDoesNotExist("Setting %s does not exists" %key)
        self.source[key] = value
        db.session.commit()


def get_active_settings_profile():
    active_settings_profile = SettingsProfile.query.filter(SettingsProfile.is_active==True).one()
    return active_settings_profile

current_settings_profile= LocalProxy(lambda: get_active_settings_profile())
current_settings = LocalProxy(lambda: Settings(get_active_settings_profile().settings))


@editable_settings.record_once
def remove_obsolete_settings(state):
    """Remove unused, persistent, settings when the application is starting.
    Effectively cleaning the editable_settings table.
    """
    with state.app.app_context():
        # sqlalchemy raises exceptions if the tables have not been created
        # so we degrade gracefully
        try:
            settings = get_active_settings_profile().settings
        except SQLAlchemyError:
            return
        to_remove = []
        for setting in settings:
            if setting not in current_app.provided_settings:
                to_remove.append(setting)
        for k in to_remove:
            del settings[k]
        db.session.commit()


@editable_settings.app_context_processor
def inject_settings():
    return dict(
        settings_profile=current_settings_profile,
        settings=current_settings
    )
