from collections import OrderedDict

# Module system
EXCLUDED_MODULES = []

# Flask SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask security
SECURITY_PASSWORD_HASH = "bcrypt"
SECURITY_USER_IDENTITY_ATTRIBUTES = ["email", "user_name"]
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = True
SECURITY_RESET_URL = "/reset-password/"

# Abstract models

# Flask Babel support
DEFAULT_LOCALE = "en"
SUPPORTED_LOCALES = OrderedDict((("en", "English"),))

# Oy specific configurations
STARLIT_LOAD_SETTINGS_JSON = False
