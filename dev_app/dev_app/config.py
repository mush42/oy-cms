#-*-coding: utf-8-*-
"""
dev_app configuration file
"""

import os


def getenvar(name, default=None):
    """Return the environment variable named `name`
        or `default` else raise RuntimeError
    """
    var = os.getenv(name, None)
    if var is None:
        if default is not None:
            return default
        else:
            raise RuntimeError(
                f"Variable {name} was not found among current "
                "environment variables and no default has been supplied"
            )
    if var in ('True', 'False'):
        return True if var == 'True' else False
    return var


DEBUG = getenvar('DEV_APP_DEBUG', False)
SECRET_KEY = getenvar('DEV_APP_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = getenvar('DEV_APP_DB_URI', 'sqlite:///:memory:')
SECURITY_PASSWORD_SALT = getenvar('DEV_APP_PASSWORD_SALT')
HOME_PAGE_TEMPLATE = "dev_app/home.html"

if DEBUG:
    path = os.path.abspath(os.path.join(os.getcwd(), "media"))
    DEPOT_STORAGES = {
        "media_storage": {"depot.storage_path": path},
    }