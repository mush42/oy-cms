from starlit.babel import gettext, lazy_gettext


DEFAULT_SETTINGS_CATEGORIES = dict(
    general={"label": lazy_gettext("General"), "icon": "fa-book"},
)

# Page
HOME_SLUG = u'index'

# Forms
FORM_UPLOADS_PATH = "uploads"

# User Profile
PROFILE_EXTRA_FIELDS = []

# Files
UPLOADS_PATH = ""
ALLOWED_EXTENSIONS = {'jpg', 'png', 'gif', 'svg', 'ico', 'mp3', 'mp4', 'webma', 'm4a', 'flv', 'doc', 'docx', 'pdf'}
