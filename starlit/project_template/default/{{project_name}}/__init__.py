# -*-coding: utf-8-*-
"""
    {{ project_name }}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A starllit-cms project
"""

from starlit import create_app
from starlit.contrib.admin import StarlitAdmin
from starlit.contrib.flask_security_templates import FlaskSecurityTemplates
from starlit.contrib.page import Page
from starlit.contrib.form import Form
from starlit.contrib.user_profile import UserProfile
from starlit.contrib.bs4 import BS4

# Create our starlit app
app = create_app("{{project_name}}", "config.py", template_folder="templates")

# Register the admin plugin
admin = StarlitAdmin(app, auto_register_modules=True)

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

