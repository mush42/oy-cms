# -*-coding: utf-8-*-
"""
    [[ project_name ]]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An Oy-cms project
"""

from oy import create_app
from oy.contrib.admin import OyAdmin
from oy.contrib.flask_security_templates import FlaskSecurityTemplates
from oy.contrib.form_fields import OyFormFields
from oy.contrib.richtext_page import RichTextPage
from oy.contrib.form import Form
from oy.contrib.user_profile import UserProfile
from oy.contrib.bs4 import BS4
from oy.contrib.redirects import Redirects
from oy.contrib.demo_content import DemoContent


# Create our oy app
app = create_app(
    "[[ project_name ]]",
    "config.py",
    template_folder="templates",
    static_folder="static"
)

# Register the admin plugin
admin = OyAdmin(app, auto_register_modules=True)

# Bootstrap 4 templates
BS4(app)

# Provides a simple implmentation of a page having a rich text content
RichTextPage(app)

# Enable you to create forms for visiters to fill-in
form = Form(app)

# Custom user profiles
UserProfile(app)

# Styled pages for login and registration
FlaskSecurityTemplates(app)

# Adds shell commands to install demo data
DemoContent(app)

# Allows you to setup custom redirects
Redirects(app)

# Provides custom wtform fields
OyFormFields(app)
