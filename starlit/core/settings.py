from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.local import LocalProxy
from flask import current_app
from starlit.boot.sqla import db
from starlit.wrappers import StarlitModule
from starlit.exceptions import SettingDoesNotExist
from starlit.models.settings import SettingsProfile


class Settings(object):
    def __init__(self, source):
        self.source = source

    def __getattr__(self, key):
        if key in self.source:
            return self.source[key]
        elif key in current_app._provided_settings:
            self.edit(key, current_app._provided_settings[key].default)
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
