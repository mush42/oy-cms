from collections import OrderedDict

# Flask generic
SECRET_KEY = 'my-secret-key'

# Module system
EXCLUDED_MODULES = []

# Flask SQLAlchemy
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask security
SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
LOGIN_USER_TEMPLATE = 'starlit/security/login.html'
SECURITY_USER_IDENTITY_ATTRIBUTES = ['email', 'user_name']
SECURITY_POST_LOGIN_VIEW = '/admin'
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = True
SECURITY_RESET_URL = '/reset-password/'

# Abstract models
ALLWAYS_UPDATE_SLUGS = False

# Flask Babel support
DEFAULT_LOCALE = 'en'
SUPPORTED_LOCALES = OrderedDict((
    ('en', 'English'),
    ('ar', 'Arabic')
))
DEFAULT_LOCALE = 'en'

# Starlit specific configurations
UPLOADS_PATH = ""
FILES_URL_PREFIX = ""

# Images
IMAGES_URL = '/images'
IMAGES_PATH = 'static'