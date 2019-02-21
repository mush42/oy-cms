from itertools import chain
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.local import LocalProxy
from flask import current_app
from oy.boot.sqla import db
from oy.wrappers import OyModule
from oy.exceptions import SettingDoesNotExist
from oy.models.settings import Setting, SettingsProfile


class Settings(object):
    def __init__(self, storage):
        self.storage = storage

    def __getattr__(self, key):
        if key in self.storage:
            return self.storage[key]
        app_settings = chain.from_iterable(current_app.provided_settings_dict.values())
        for setting in app_settings:
            if setting["name"] == key:
                self.edit(key, setting["default"])
                return setting["default"]
        raise SettingDoesNotExist("Setting %s does not exists" % key)

    def __setattribute__(self, key, value):
        raise AttributeError("Can't set attribute")

    def edit(self, key, value):
        self.storage.store[key] = Setting(key=key, value=value)
        db.session.commit()


def get_active_settings_profile():
    active_settings_profile = SettingsProfile.query.filter(
        SettingsProfile.is_active == True
    ).one()
    return active_settings_profile


current_settings_profile = LocalProxy(lambda: get_active_settings_profile())
current_settings = LocalProxy(lambda: Settings(get_active_settings_profile().settings))
