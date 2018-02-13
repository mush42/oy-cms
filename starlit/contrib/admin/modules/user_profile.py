from collections import OrderedDict
from flask import current_app, request, url_for, flash, redirect
from flask_security import current_user
from flask_security.utils import logout_user
from flask_admin import expose
from flask_admin import form
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup

from starlit.boot.exts.sqla import db
from starlit.boot.exts.security import user_datastore
from starlit.babel import gettext, lazy_gettext
from starlit.modules.core.models.user import User, Role
from starlit.util.wtf import FileSelectorField
from starlit.util.dynamicform import DynamicForm
from starlit.modules.user_profile.models import Profile
from ..plugin import AdminPlugin
from ..core import StarlitModelView


class BaseUserAdmin(StarlitModelView):
    def is_accessible(self):
        return current_user.has_role('admin')

class UserAdmin(BaseUserAdmin):
    list_template = 'starlit_admin/user/list.html'
    can_create = False
    column_exclude_list = ['password', 'slug', 'profile']
    form_excluded_columns = ['password', 'posts', 'profile', 'confirmed_at', 'slug']
    column_extra_row_actions = [
        EndpointLinkRowAction(icon_class="fa fa-lock", endpoint='.change_password', title=lazy_gettext("Change Password"), id_arg='pk'),
    ]

    @expose('/<int:pk>/deactivate/', methods=['GET', 'POST'])
    def deactivate_user(self, pk):
        if user.is_active:
            user = self.get_one(str(pk))
            user.is_active = False
            db.session.commit()
            flash(gettext('Account deactivated successfully'))
        return redirect(url_for('.index_view'))

    @expose('/<int:pk>/activate/', methods=['GET', 'POST'])
    def activate_user(self, pk):
        user = self.get_one(str(pk))
        if not user.is_active:
            user.is_active = True
            db.session.commit()
            flash(gettext('Account activated successfully'))
        return redirect(url_for('.index_view'))


class ProfileAdmin(BaseUserAdmin):

    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        for field in form:
            if field.name.startswith('profile_extra__'):
                field.data = model.get(field.name[15:])

    def after_model_change(self, form, model, is_created):
        for field in form:
            if field.name.startswith('profile_extra__'):
                model[field.name[15:]] = field.data
        db.session.commit()

    @property
    def form_extra_fields(self):
        """Contribute the fields of profile extras"""
        rv = OrderedDict() #(image_path=FileSelectorField(label=lazy_gettext('Profile Picture'), button_text=lazy_gettext('Select Profile Picture')))
        extra_fields = list(current_app.config.get('PROFILE_EXTRA_FIELDS', []))
        for field in DynamicForm(fields=extra_fields, with_admin=True).fields:
            rv.setdefault('profile_extra__%s' %field[0], field[1])
        return rv

    def todo_list_thumbnail(view, context, model, name):
        if not model.image_path:
            return Markup('<span class="fa fa-2x fa-user"></span>')
        return Markup('<img src="%s" class="img-thumbnail img-circle" style="max-width:75px;max-height:75px;" />' % model.image.src)
                                 
    can_create = False
    can_delete = False
    column_exclude_list = ['user', 'created', 'extras']
    column_list = ['image_path', 'first_name', 'last_name', 'updated']
    #column_formatters = dict(image_path=_list_thumbnail)
    form_excluded_columns = ['user', 'image_description', 'extras', 'updated', 'created']

class RoleAdmin(BaseUserAdmin):
    column_exclude_list = ['user']


@AdminPlugin.setupmethod
def register_admin_pages(app, admin):
    with app.app_context():
        admin.add_view(UserAdmin(User, db.session, name=lazy_gettext('User Accounts'), category=lazy_gettext('Users'), menu_icon_type='fa', menu_icon_value='fa-shield'))
        admin.add_view(ProfileAdmin(Profile, db.session, name=lazy_gettext('Profiles'), category=lazy_gettext('Users'), menu_icon_type='fa', menu_icon_value='fa-user'))
        admin.add_view(RoleAdmin(Role, db.session, name=lazy_gettext('Roles & Permissions'), category=lazy_gettext('Users'), menu_icon_type='fa', menu_icon_value='fa-lock'))
