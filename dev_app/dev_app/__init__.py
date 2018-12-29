# -*-coding: utf-8-*-
"""
    dev_app
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A starllit-cms project
"""

from oy import create_app
from oy.contrib.admin import OyAdmin
from oy.contrib.flask_security_templates import FlaskSecurityTemplates
from oy.contrib.page import Page
from oy.contrib.form import Form
from oy.contrib.user_profile import UserProfile
from oy.contrib.bs4 import BS4

# Create our oy app
app = create_app("dev_app", "config.py", template_folder="templates")

# Register the admin plugin
admin = OyAdmin(app, auto_register_modules=True)

# Bootstrap 4 templates
BS4(app)

# Provides basic templates for rendering the CMS pages
Page(app)

# Enable you to create user forms
form = Form(app)

# Custom user profiles
UserProfile(app)

# Styled pages for login and registration
FlaskSecurityTemplates(app)