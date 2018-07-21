from flask import request, url_for
from flask_admin import Admin, helpers as admin_helpers
from starlit.babel import lazy_gettext, gettext, ngettext
from .wrappers import StarlitIndexView
from .core import register_settings_admin
from .resource_module import admin_resource_module


def security_ctp_with_admin(admin):
    def security_context_processor():
        if not request.blueprint == 'security':
            return {}
        return dict(
            admin_base_template=admin.base_template,
            admin_view=admin.index_view,
            h=admin_helpers,
            get_url=url_for,
            _gettext= gettext,
            _trans= gettext
        )
    return security_context_processor


class StarlitAdmin(Admin):
    """Provides integration with Flask-Admin"""

    def __init__(self, app=None, **kwargs):
        index_view = kwargs.pop('index_view', StarlitIndexView(
            menu_icon_type='fa', menu_icon_value='fa-home',
            template='starlit_admin/index.html')
        )
        self.resource_module = kwargs.pop('resource_module', admin_resource_module)
        defaults = {
            'name': lazy_gettext('Dashboard'),
            'template_mode': 'bootstrap3',
            'base_template': 'starlit_admin/master.html',
            'index_view': index_view,
            'category_icon_classes': {'Settings': 'fa fa-cog', 'Pages':'fa fa-file-text-o', 'Users': 'fa fa-users', 'Blog': 'fa fa-link'}
        }
        for k, v in defaults.items():
            kwargs.setdefault(k, v)
        return super(StarlitAdmin, self).__init__(app, **kwargs)

    def _init_extension(self):
        super(StarlitAdmin, self)._init_extension()
        self.app.register_module(self.resource_module)
        register_settings_admin(self.app, self)
        self.app.context_processor(security_ctp_with_admin(self))
        self.app.context_processor(lambda: {"admin_plugin_static": self.admin_plugin_static})
        if 'SECURITY_POST_LOGIN_VIEW' not in self.app.config:
            self.app.config['SECURITY_POST_LOGIN_VIEW'] = self.url

    def admin_plugin_static(self, filename):
        return url_for(
            "%s.static" %('starlit-admin'),
            filename="starlit-admin/%s" %(filename,)
        )

