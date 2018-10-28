# -*-coding: utf-8-*-
"""
boycott configuration file
"""
import os

print(os.getcwd())


def getenvar(name, default=None):
    """Return the environment variable named `name` or `default` else raise RuntimeError"""
    val = os.getenv(name, default)
    if not val:
        raise RuntimeError(
            f"Variable {name} was not found among current environment variables and no default has been supplied"
        )
    return val


DEBUG = getenvar("BOYCOTT_DEBUG", True)
SECRET_KEY = getenvar("BOYCOTT_SECRET_KEY")
SQLALCHEMY_DATABASE_URI = getenvar("BOYCOTT_DB_URI", "sqlite:///:memory:")
# EXPLAIN_TEMPLATE_LOADING=True,
SECURITY_PASSWORD_SALT = getenvar("BOYCOTT_PASSWORD_SALT")
STARLIT_LOAD_SETTINGS_JSON = True
