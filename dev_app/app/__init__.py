from flask import render_template
from starlit import create_app
from starlit.babel import lazy_gettext
from starlit.contrib.admin import StarlitAdmin
from starlit.contrib.flask_security_templates import FlaskSecurityTemplates
from starlit.contrib.page import Page
from starlit.contrib.form import Form
from starlit.contrib.user_profile import UserProfile
from starlit.contrib.bs4 import BS4
from .module import module


app = create_app(__name__, "config.py", template_folder="templates")
admin = StarlitAdmin(app, auto_register_modules=True)
form = Form(app)
FlaskSecurityTemplates(app)
Page(app)
BS4(app)

UserProfile(app, profile_fields=(
    dict(
        name="first_name",
        type="text",
        label=lazy_gettext("First name"),
        required=True
    ),
    dict(
        name="last_name",
        type="text",
        label=lazy_gettext("Last name"),
        required=True
    ),
    dict(
        name="user_bio",
        type="textarea",
        label=lazy_gettext("Biography"),
    ),
))


app.register_module(module)
