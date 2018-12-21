# -*-coding: utf-8-*-
"""
    {{ project_name }}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A starllit-cms project
"""

from starlit import create_app
from starlit.contrib.admin import StarlitAdmin
from starlit.contrib.security_template_module import security_template_module
from starlit.contrib.page import page

from starlit.contrib.form import Form
from starlit.contrib.user_profile import UserProfile


# Create our starlit app
app = create_app("{{project_name}}", "config.py", template_folder="templates")

# Register the admin plugin
admin = StarlitAdmin(app, auto_register_modules=True)

# Enable you to create user forms 
form = Form(app)

# Custom user profiles
UserProfile(app)

# Styled pages for login and registration
app.register_module(security_template_module)

# Provides basic templates for rendering the CMS pages
app.register_module(page)
