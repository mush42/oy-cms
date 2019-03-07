from functools import wraps
from flask import flash, request, redirect, url_for, abort
from flask_admin import Admin, expose, BaseView
from flask_admin.base import BaseView, AdminIndexView
from flask_admin.form import SecureForm
from flask_admin.helpers import get_redirect_target
from flask_admin.model.template import (
    DeleteRowAction,
    LinkRowAction,
    EndpointLinkRowAction,
)
from flask_admin.contrib.sqla import ModelView, form
from flask_security import current_user
from oy.boot.sqla import db
from oy.babel import gettext, lazy_gettext


class AuthenticationViewMixin:
    """Basic permissions for oy views."""

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False
        if current_user.has_role("staff"):
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        if current_user.is_authenticated:
            abort(403)
        else:
            return redirect(url_for("security.login", next=request.url))


class OyDeleteRowAction(EndpointLinkRowAction):
    def __init__(self):
        super().__init__(
            "fa fa-trash",
            ".delete_confirm",
            title=lazy_gettext("Delete record"),
            id_arg="pk",
        )


class OyModelFormConverter(form.AdminModelConverter):
    def _get_label(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get("label"):
            return info["label"]
        return super(OyModelFormConverter, self)._get_label(name, field_args)

    def _get_description(self, name, field_args):
        info = getattr(self.view.model, name).info
        if info.get("description"):
            return info["description"]
        return super(OyModelFormConverter, self)._get_description(name, field_args)


class OyModelView(AuthenticationViewMixin, ModelView):
    """The base view class for all oy model views."""

    model_form_converter = OyModelFormConverter

    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop("verbose_name", kwargs.get("name"))
        self.show_in_menu = kwargs.pop("show_in_menu", True)
        super().__init__(*args, **kwargs)

    def get_column_name(self, field):
        if self.column_labels and field in self.column_labels:
            return self.column_labels[field]
        column = self.model.__mapper__.columns.get(field)
        if column is not None and column.info.get("label"):
            return column.info["label"]
        return super(OyModelView, self).get_column_name(field)

    def get_list_row_actions(self):
        actions = super().get_list_row_actions()
        if self.can_delete:
            actions = [a for a in actions if not isinstance(a, DeleteRowAction)]
            actions.append(OyDeleteRowAction())
        if hasattr(self, "get_preview_url"):
            actions.append(
                LinkRowAction(
                    icon_class="fa fa-eye",
                    url=lambda v, i, r: self.get_preview_url(r),
                    title=lazy_gettext("Preview in site"),
                )
            )
        return actions

    @expose("/delete-confirm/<int:pk>")
    def delete_confirm(self, pk):
        if not self.can_delete:
            abort(404)
        obj = self.get_one(str(pk))
        if obj is not None:
            endpoint = ".index_view" if self.show_in_menu else "admin.index"
            return_url = get_redirect_target() or url_for(endpoint)
            return self.render(
                "admin/oy/delete_confirm.html", pk=pk, return_url=return_url
            )
        else:
            abort(404)

    @expose("/do-delete/<string:pk>")
    def delete_executor(self, pk):
        if not self.can_delete:
            abort(404)
        obj = self.get_one(pk)
        if obj is not None:
            db.session.delete(obj)
            db.session.commit()
            flash("Record deleted successfully.")
            endpoint = ".index_view" if self.show_in_menu else "admin.index"
            return redirect(get_redirect_target() or url_for(endpoint))
        else:
            abort(404)


class OyIndexView(AuthenticationViewMixin, AdminIndexView):
    @expose("/")
    def index(self):
        return super(OyIndexView, self).index()


class OyBaseView(BaseView, AuthenticationViewMixin):
    def __init__(self, *args, **kwargs):
        self.verbose_name = kwargs.pop("verbose_name", kwargs.get("name"))
        self.show_in_menu = kwargs.pop("show_in_menu", True)
        super().__init__(*args, **kwargs)


def admin_required(f):
    @wraps(f)
    def _decorated(*args, **kw):
        if not AuthenticationViewMixin().is_accessible():
            abort(404)
        return f(*args, **kw)

    return _decorated
