# -*-coding: utf-8-*-
"""
    [[ project_name ]]
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    An Oy-CMS project.
"""

from oy import prepare_app
from oy.contrib.admin import OyAdmin
from oy.contrib.flask_security_templates import FlaskSecurityTemplates
from oy.contrib.bootstrap4 import Bootstrap4
from oy.contrib.users import UserManager
from oy.contrib.redirects import Redirects
from oy.contrib.form import Form
from oy.contrib.media import Media
from oy.contrib.demo_content import DemoContent
from .home_page import home_page


def create_app():
    # Create our oy app
    app = prepare_app(
        "[[ project_name ]]", "config.py", template_folder="templates", static_folder="static"
    )

    # Flask-admin
    admin = OyAdmin(app, auto_register_modules=True)

    # User management with flexible user profiles
    UserManager(app)

    # Styled pages for login and registration
    FlaskSecurityTemplates(app)

    # Bootstrap 4 templates
    Bootstrap4(app)

    # Enable you to create forms for visiters to fill-in
    form = Form(app)

    # User uploaded images and documents
    Media(app, serve_files=True)

    # Adds shell commands to install demo data
    DemoContent(app)

    # Allows you to setup custom redirects
    Redirects(app)

    # Register the home page module
    app.register_module(home_page)

    return app
