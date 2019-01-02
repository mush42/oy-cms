from functools import partial
from werkzeug import import_string
from flask import g, request, url_for
from flask_admin import Admin, helpers as admin_helpers
from oy.babel import lazy_gettext, gettext, ngettext
from .wrappers import OyIndexView
from .core import register_page_admin, register_settings_admin
from .resource_module import admin_resource_module


def security_ctp_with_admin(admin):
    def security_context_processor():
        if not request.blueprint == "security":
            return {}
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for,
            _gettext=gettext,
            _trans=gettext,
        )

    return security_context_processor


class OyAdmin(Admin):
    """Provides integration with Flask-Admin"""

    # Resource module that provides templates and static files
    resource_module = admin_resource_module

    def __init__(self, app=None, auto_register_modules=False, **kwargs):
        index_view = kwargs.pop(
            "index_view",
            OyIndexView(
                menu_icon_type="fa",
                menu_icon_value="fa-home",
                # template="oy_admin/index.html",
            ),
        )
        self.auto_register_modules = auto_register_modules
        defaults = {
            "name": lazy_gettext("Dashboard"),
            "template_mode": "bootstrap3",
            # "base_template": "oy_admin/master.html",
            "index_view": index_view,
            "category_icon_classes": {
                "Settings": "fa fa-cog",
                "Pages": "fa fa-file-text-o",
                "Users": "fa fa-users",
            },
        }
        for k, v in defaults.items():
            kwargs.setdefault(k, v)
        super(OyAdmin, self).__init__(app, **kwargs)

    def _init_extension(self):
        super(OyAdmin, self)._init_extension()
        self.app.register_module(self.resource_module)
        register_page_admin(self.app, self)
        # TODO: Fix this hack
        regsettings = partial(register_settings_admin, self.app, self)
        self.app.before_first_request(regsettings)
        self.app.add_template_filter(lambda l: set(l), name="remove_double")
        self.app.context_processor(security_ctp_with_admin(self))
        self.app.context_processor(
            lambda: {
                "admin_plugin_static": self.admin_plugin_static,
                "add_field_static": self.add_form_field_static,
            }
        )
        self.app.config["SECURITY_POST_LOGIN_VIEW"] = self.url
        if self.auto_register_modules:
            self.app.before_first_request(self.register_module_admin)

    def admin_plugin_static(self, filename):
        return url_for(
            "oy.contrib.admin.resource_module.static",
            filename="oy-admin/%s" % (filename),
        )

    def add_form_field_static(self, field):
        if getattr(g, "form_field_static", None) is None:
            g.form_field_static = {"css": [], "js": []}
        for filetype in ("css", "js"):
            files = getattr(field.Meta, f"extra_{filetype}", [])
            if callable(files):
                files = files(field)
            g.form_field_static[filetype].extend(files)

    def register_module_admin(self):
        for module in self.app.modules.values():
            func_name = module.import_name + ":register_admin"
            admin_func = import_string(func_name, silent=True)
            if admin_func is not None:
                admin_func(self.app, self)
