import os
from flask import current_app, request, url_for
from flask_admin import expose
from flask_admin.contrib.fileadmin import FileAdmin
from flask_admin import form
from jinja2 import Markup

from starlit.boot.exts.sqla import db
from starlit.babel import gettext, lazy_gettext
from starlit.boot.exts.admin import admin, AuthenticationViewMixin
from . import files

class StarlitFileAdmin(AuthenticationViewMixin, FileAdmin):
    rename_modal = True
    list_template = 'starlit/admin/files/list.html'



@files.after_setup
def register_admin(app):
    StarlitFileAdmin.allowed_extensions = app.config.get("ALLOWED_EXTENSIONS", set())
    admin.add_view(StarlitFileAdmin(app.config['UPLOADS_PATH'], base_url='/files/', name=lazy_gettext('Files'), url='files', menu_icon_type='fa', menu_icon_value='fa-folder'))