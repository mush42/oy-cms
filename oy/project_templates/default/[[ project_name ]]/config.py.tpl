# -*-coding: utf-8-*-
"""
[[ project_name ]] configuration file
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
    if var in ("True", "False"):
        return True if var == "True" else False
    return var


DEBUG = getenvar("[[ project_name ]]_DEBUG", False)
SECRET_KEY = getenvar("[[ project_name ]]_SECRET_KEY")
SQLALCHEMY_DATABASE_URI = getenvar("[[ project_name ]]_DB_URI", "sqlite:///:memory:")
SECURITY_PASSWORD_SALT = getenvar("[[ project_name ]]_PASSWORD_SALT")

# Depot storage config for user uploaded files
DEPOT_MEDIA_STORAGES = dict(
    media_storage={"depot.storage_path": os.path.abspath(os.path.join(os.getcwd(), "media"))}
)
