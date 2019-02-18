# -*- coding: utf-8 -*-
"""
    oy.contrib.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Adds the admin dashboard via Flask Admin.

    :copyright: (c) 2019 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from functools import partial
from wtforms.form import BaseForm
from jinja2 import Markup, contextfunction
from werkzeug import import_string
from flask import request, url_for, abort
from flask_admin import Admin, expose, helpers as admin_helpers
from oy.wrappers import OyModule
from oy.babel import lazy_gettext, gettext, ngettext
from oy.signals import oy_app_starting
from .wrappers import (
    admin_required,
    AuthenticationViewMixin,
    OyModelView,
    OyBaseView,
    OyIndexView,
)
from .displayable_admin import DisplayableAdmin
from .page_admin import PageAdmin
from .settings_admin import register_settings_admin


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


default_resource_module = OyModule(
    name="oy-admin-resource-module",
    import_name=__name__,
    template_folder="templates",
    static_folder="static",
    static_url_path="/admin/static/assets",
)


class OyAdmin(Admin):
    """Provides integration with Flask-Admin"""

    # Resource module that provides custom admin templates and static files
    resource_module = default_resource_module

    def __init__(self, app=None, auto_register_modules=False, **kwargs):
        index_view = kwargs.pop(
            "index_view",
            OyIndexView(
                name=lazy_gettext("Dashboard Home"),
                menu_icon_type="fa",
                menu_icon_value="fa-dashboard",
                template="oy/contrib/admin/index.html",
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
        self.app.config["SECURITY_POST_LOGIN_VIEW"] = self.url
        if "oy-admin-resource-module" not in self.app.modules:
            self.app.register_module(self.resource_module)
        oy_app_starting.connect(self.finalization_tasks, sender=self.app)
        [
            self.app.context_processor(func)
            for func in (
                security_ctp_with_admin(self),
                lambda: dict(
                    oy_admin_static=self.admin_plugin_static,
                    get_form_css=self.get_form_static("css"),
                    get_form_js=self.get_form_static("js"),
                ),
            )
        ]

    def finalization_tasks(self, sender):
        self._secure_admin_static_files()
        register_settings_admin(self.app, self)
        if self.auto_register_modules:
            self.register_module_admin()

    def _secure_admin_static_files(self):
        for rule in self.app.url_map.iter_rules():
            endpoint = rule.endpoint
            if "admin" in endpoint and endpoint.endswith(".static"):
                func = self.app.view_functions[endpoint]
                self.app.view_functions[endpoint] = admin_required(func)

    def _get_static_for_field(self, field, type_):
        files = getattr(field, f"get_field_{type_}", [])
        if callable(files):
            files = files()
        return files

    def get_form_static(self, type_):
        @contextfunction
        def form_static_getter(context):
            rv = [] if type_ == "css" else dict(urls=[], markup=[])
            for form in (v for v in context.values() if isinstance(v, BaseForm)):
                for field in form:
                    for asset in (
                        asst
                        for asst in self._get_static_for_field(field, type_)
                        if asst not in rv
                    ):
                        if type_ == "css":
                            rv.append(asset)
                        else:
                            key = "markup" if type(asset) is Markup else "urls"
                            rv[key].append(asset)
            return rv

        return form_static_getter

    def admin_plugin_static(self, filename):
        return url_for("oy-admin-resource-module.static", filename=filename)

    def register_module_admin(self):
        for module in self.app.modules.values():
            func_name = module.import_name + ":register_admin"
            admin_func = import_string(func_name, silent=True)
            if admin_func is not None:
                admin_func(self.app, self)
