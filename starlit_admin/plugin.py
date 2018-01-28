from flask import request, url_for
from flask_admin import Admin, helpers as admin_helpers
from starlit.plugin import StarlitPlugin 
from starlit_admin.core import StarlitIndexView
from starlit.babel import lazy_gettext, gettext, ngettext


def security_ctp_with_aadmin(admin):
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


class AdminPlugin(StarlitPlugin):
    """Provides integration with Flask-Admin"""
    setupmethods = set()
    identifier = "starlit_admin"
    needs_blueprint_registration = True
    blueprint_opts = dict(
        name="starlit_admin",
        import_name="starlit_admin",
        static_folder="static",
        template_folder="templates",
    )

    def init_app(self, app, *args, **kwargs):
        admin = self.setup_flaskadmin(app)
        app.admin = admin
        self.static_url_path = "/{}".format(self.name.replace("_", "-"))
        app.context_processor(security_ctp_with_aadmin(admin))
        app.context_processor(lambda: {"admin_plugin_static": self.admin_plugin_static})
        for func in self.setupmethods:
            func(app, admin)

    @classmethod
    def setupmethod(cls, func):
        cls.setupmethods.add(func)
        def wrapped(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapped

    def setup_flaskadmin(self, app):
        index_view = StarlitIndexView(
            menu_icon_type='fa', menu_icon_value='fa-home',
            template='starlit_admin/index.html')
        admin = Admin(app,
            name=lazy_gettext('Dashboard'),
            template_mode='bootstrap3',
            base_template='starlit_admin/master.html',
            index_view=index_view,
            category_icon_classes={'Settings': 'fa fa-cog', 'Pages':'fa fa-file-text-o', 'Users': 'fa fa-users', 'Blog': 'fa fa-link'}
        )
        return admin

    def admin_plugin_static(self, filename):
        return url_for("{}.static".format(self.name), filename="starlit-admin/{}".format(filename))
