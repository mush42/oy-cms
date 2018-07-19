#-*-coding: utf-8-*-
"""
{{ project_name }} configuration file
"""
import os
{% set PROJECT_NAME = project_name|upper %}

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


DEBUG = getenvar('{{ PROJECT_NAME }}_DEBUG', False)
SECRET_KEY = getenvar('{{ PROJECT_NAME }}_SECRET_KEY')
SQLALCHEMY_DATABASE_URI = getenvar('{{ PROJECT_NAME }}_DB_URI', get_db_uri())
SECURITY_PASSWORD_SALT = getenvar('{{ PROJECT_NAME }}_PASSWORD_SALT')
