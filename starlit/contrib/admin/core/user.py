from collections import OrderedDict
from flask import request, url_for, flash, redirect
from flask_security import current_user
from flask_security.utils import logout_user
from flask_admin import expose
from flask_admin import form
from flask_admin.model.form import InlineFormAdmin
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.contrib.sqla import ModelView
from flask_security.changeable import change_user_password
from jinja2 import Markup
from .. import app, db
from ..main import user_datastore
from ..babel import gettext, lazy_gettext
from ..user.models import User, Profile, Role
from ..util.wtf import FileSelectorField
from ..util.dynamicform import DynamicForm
from ..util.forms.register import CanellaRegisterForm, register_user
from ..util.forms.change_password import CanellaChangePasswordForm, change_password
from . import admin, CanellaModelView


class BaseUserAdmin(CanellaModelView):
    def is_accessible(self):
        return current_user.has_role("admin")


class UserAdmin(BaseUserAdmin):
    list_template = "canella/admin/user/list.html"
    can_create = False
    column_exclude_list = ["password", "slug", "profile"]
    form_excluded_columns = ["password", "posts", "profile", "confirmed_at", "slug"]
    column_extra_row_actions = [
        EndpointLinkRowAction(
            icon_class="fa fa-lock",
            endpoint=".change_password",
            title=lazy_gettext("Change Password"),
            id_arg="pk",
        )
    ]

    @expose("/<int:pk>/change-password/", methods=["GET", "POST"])
    def change_password(self, pk):
        user = self.get_one(str(pk))
        form = CanellaChangePasswordForm(user=user)
        if form.validate_on_submit():
            change_password(user, form.password.data)
            db.session.commit()
            if user.email == current_user.email:
                logout_user()
            flash(gettext("Password changed successfully"))
            return redirect(url_for(".index_view"))
        return self.render("admin/model/create.html", form=form)

    @expose("/<int:pk>/deactivate/", methods=["GET", "POST"])
    def deactivate_user(self, pk):
        if user.is_active:
            user = self.get_one(str(pk))
            user.is_active = False
            db.session.commit()
            flash(gettext("Account deactivated successfully"))
        return redirect(url_for(".index_view"))

    @expose("/<int:pk>/activate/", methods=["GET", "POST"])
    def activate_user(self, pk):
        user = self.get_one(str(pk))
        if not user.is_active:
            user.is_active = True
            db.session.commit()
            flash(gettext("Account activated successfully"))
        return redirect(url_for(".index_view"))

    @expose("/register/", methods=["GET", "POST"])
    def register(self):
        form = CanellaRegisterForm()
        if form.validate_on_submit():
            should_confirm = form.send_confirmation.data
            del form.send_confirmation
            register_user(should_confirm=should_confirm, **form.to_dict())
            return redirect(url_for(".index_view"))
        return self.render("admin/model/create.html", form=form)


class ProfileAdmin(BaseUserAdmin):
    def on_form_prefill(self, form, id):
        model = self.get_one(id)
        for field in form:
            if field.name.startswith("profile_extra__"):
                field.data = model.get(field.name[15:])

    def after_model_change(self, form, model, is_created):
        for field in form:
            if field.name.startswith("profile_extra__"):
                model[field.name[15:]] = field.data
        db.session.commit()

    @property
    def form_extra_fields(self):
        """Contribute the fields of profile extras"""
        rv = OrderedDict(
            image_path=FileSelectorField(
                label=lazy_gettext("Profile Picture"),
                button_text=lazy_gettext("Select Profile Picture"),
            )
        )
        extra_fields = list(app.config.get("PROFILE_EXTRA_FIELDS", []))
        for field in DynamicForm(extra_fields, with_admin=True).fields:
            rv.setdefault("profile_extra__%s" % field[0], field[1])
        return rv

    def _list_thumbnail(view, context, model, name):
        if not model.image_path:
            return Markup('<span class="fa fa-2x fa-user"></span>')
        return Markup(
            '<img src="%s" class="img-thumbnail img-circle" style="max-width:75px;max-height:75px;" />'
            % model.image.src
        )

    can_create = False
    can_delete = False
    column_exclude_list = ["user", "created", "extras"]
    column_list = ["image_path", "first_name", "last_name", "updated"]
    column_formatters = dict(image_path=_list_thumbnail)
    form_excluded_columns = [
        "user",
        "image_description",
        "extras",
        "updated",
        "created",
    ]


class RoleAdmin(BaseUserAdmin):
    column_exclude_list = ["user"]


admin.add_view(
    UserAdmin(
        User,
        db.session,
        name=lazy_gettext("User Accounts"),
        category=lazy_gettext("Users"),
        menu_icon_type="fa",
        menu_icon_value="fa-shield",
    )
)
admin.add_view(
    ProfileAdmin(
        Profile,
        db.session,
        name=lazy_gettext("Profiles"),
        category=lazy_gettext("Users"),
        menu_icon_type="fa",
        menu_icon_value="fa-user",
    )
)
admin.add_view(
    RoleAdmin(
        Role,
        db.session,
        name=lazy_gettext("Roles & Permissions"),
        category=lazy_gettext("Users"),
        menu_icon_type="fa",
        menu_icon_value="fa-lock",
    )
)
