#-*-coding: utf-8-*-
"""
{{ appname }} configuration file
"""
import os
{% set APP_NAME = appname|capitalize %}

def getenvar(name, default=None):
    """Return the environment variable named `name`
        or `default` else raise RuntimeError
    """
    val = os.getenv(name, default)
    if not val:
        raise RuntimeError(
            f"Variable {name} was not found among current "
            "environment variables and no default has been supplied"
        )
    return val

def get_db_uri():
    return os.path.join(os.getcwd(), 'db.sqlite')


DEBUG = getenvar('{{ APP_NAME }}_DEBUG', False)
SECRET_KEY = getenvar('{{ APP_NAME }}_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = getenvar('{{ APP_NAME }}_DB_URI', get_db_uri())
SECURITY_PASSWORD_SALT = getenvar('{{ APP_NAME }}_PASSWORD_SALT')
