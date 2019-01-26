#-*-coding: utf-8-*-
"""
[[ project_name ]] configuration file
"""

import os
[% set PROJECT_NAME = project_name|upper %]

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


DEBUG = getenvar('[[ PROJECT_NAME ]]_DEBUG', False)
SECRET_KEY = getenvar('[[ PROJECT_NAME ]]_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = getenvar('[[ PROJECT_NAME ]]_DB_URI', 'sqlite:///:memory:')
SECURITY_PASSWORD_SALT = getenvar('[[ PROJECT_NAME ]]_PASSWORD_SALT')
