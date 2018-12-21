from flask import render_template
from starlit import create_app
from starlit.contrib.admin import StarlitAdmin
from starlit.contrib.security_template_module import security_template_module
from starlit.contrib.page import page

from starlit.contrib.form import Form
from starlit.contrib.user_profile import UserProfile
from .module import module


app = create_app(__name__, "config.py", template_folder="templates")
admin = StarlitAdmin(app, auto_register_modules=True)
form = Form(app)
UserProfile(app)
app.register_module(security_template_module)
app.register_module(page)
app.register_module(module)
