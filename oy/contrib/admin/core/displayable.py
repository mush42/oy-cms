from six import with_metaclass
from flask import flash, abort
from flask_admin import expose
from flask_admin.model import typefmt
from flask_admin.model.template import LinkRowAction, EndpointLinkRowAction
from flask_admin.base import AdminViewMeta
from flask_admin.form import rules
from flask_admin.form import SecureForm
from flask_admin.actions import action
from flask_admin.helpers import get_current_view
from wtforms.fields import SelectField
from datetime import date
from oy.boot.sqla import db
from oy.models.abstract import Displayable
from oy.babel import gettext, lazy_gettext
from oy.contrib.admin.wrappers import OyModelView


def status_formatter(view, context, model, name):
    status = getattr(model, name)
    return dict(Displayable.STATUS_CHOICES).get(status)


DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
DEFAULT_FORMATTERS.update({})

DISPLAYABEL_DEFAULTS = dict(
    can_view_details=False,
    page_size=10,
    column_list=("title", "status", "updated"),
    column_type_formatters=DEFAULT_FORMATTERS,
    column_formatters={"status": status_formatter},
    column_default_sort=("created", True),
    column_editable_list=("title",),
    form_columns=(
        "title",
        "status",
        "publish_date",
        "expire_date",
        "meta_title",
        "meta_description",
        "keywords",
        "should_auto_generate",
    ),
    form_excluded_columns=(
        "_sort_order",
        "sort_order",
        "site",
        "created",
        "updated",
        "versions",
        "author",
        "last_edited_by",
    ),
    form_extra_fields={
        "status": SelectField(
            label=lazy_gettext("Status"), choices=Displayable.STATUS_CHOICES
        )
    },
)

default_row_actions = (
    EndpointLinkRowAction(
        icon_class="fa fa-clock-o",
        endpoint=".versioning_index",
        title=lazy_gettext("Manage Versions"),
        id_arg="pk",
    ),
)


class DisplayableAdminType(AdminViewMeta):
    def __new__(cls, name, bases, d):
        if "DisplayableAdmin" not in [c.__name__ for c in bases]:
            return type.__new__(cls, name, bases, d)
        for key, value in DISPLAYABEL_DEFAULTS.items():
            if key not in d:
                d[key] = value
        row_actions = list(default_row_actions)
        crowactions = d.get("column_extra_row_actions", [])
        if "get_preview_url" in d:
            crowactions.append(
                LinkRowAction(
                    icon_class="fa fa-eye",
                    url=lambda v, i, r: d["get_preview_url"](r),
                    title=lazy_gettext("Preview in site"),
                )
            )
        crowactions.extend(row_actions)
        d["column_extra_row_actions"] = crowactions
        return type.__new__(cls, name, bases, d)


class DisplayableAdmin(with_metaclass(DisplayableAdminType, OyModelView)):
    def get_column_name(self, field):
        try:
            return self.model.__mapper__.columns[field].info["label"]
        except:
            return super(DisplayableAdmin, self).get_column_name(field)

    @expose("/<int:pk>/versions/")
    def versioning_index(self, pk):
        instance = self.get_one(id=str(pk))
        versions = list(instance.versions)
        versions.reverse()
        return self.render(
            "canella/admin/versioning/list.html", model=instance, versions=versions
        )

    @expose("/<int:pk>/versions/<int:version_id>/")
    def versioning_diff(self, pk, version_id):
        instance = self.get_one(str(pk))
        version = instance.versions.filter_by(transaction_id=version_id).one_or_none()
        if version is None:
            abort(404)
        return self.render(
            "canella/admin/versioning/diffs.html", model=instance, version=version
        )

    @action("publish", "Publish", "Are you sure you want to publish selected content?")
    def action_publish(self, ids):
        try:
            model = self.model
            query = model.query.filter(model.id.in_(ids))
            for instance in query.all():
                instance.status = "published"
            db.session.commit()
            flash("Content was published successfully")
        except:
            flash("Faild to publish content")
