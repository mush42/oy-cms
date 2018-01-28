from collections import OrderedDict


SECRET_KEY = 'my-secret-key'
EXCLUDED_MODULES = []
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
LOGIN_USER_TEMPLATE = 'starlit/security/login.html'
SECURITY_USER_IDENTITY_ATTRIBUTES = ['email', 'user_name']
SECURITY_POST_LOGIN_VIEW = '/admin'
SECURITY_CONFIRMABLE = False
SECURITY_RECOVERABLE = True
SECURITY_RESET_URL = '/reset-password/'

ALLWAYS_UPDATE_SLUGS = False
DEFAULT_LOCALE = 'en'
SUPPORTED_LOCALES = OrderedDict((
    ('en', 'English'),
    ('ar', 'Arabic')
))

SUPPORTED_LOCALES = OrderedDict((
    ('en', 'English'),
    ('ar', 'Arabic')
))
DEFAULT_LOCALE = 'en'