from flask import flash, abort
from flask_admin import expose
from flask_admin.model import typefmt
from flask_admin.model.template import LinkRowAction, EndpointLinkRowAction
from flask_admin.base import AdminViewMeta
from flask_admin.form import rules
from flask_admin.form import SecureForm
from flask_admin.actions import action
from flask_admin.helpers import get_current_view
from wtforms.fields import StringField, SelectField
from datetime import date
from oy.boot.sqla import db
from oy.models.abstract import Displayable
from oy.babel import gettext, lazy_gettext
from .wrappers import OyModelView


def status_formatter(view, context, model, name):
    status = getattr(model, name)
    return dict(Displayable.STATUS_CHOICES).get(status)


DEFAULT_FORMATTERS = dict(typefmt.BASE_FORMATTERS)
DEFAULT_FORMATTERS.update({})

DISPLAYABEL_DEFAULTS = dict(
    can_view_details=False,
    page_size=10,
    column_type_formatters=DEFAULT_FORMATTERS,
    column_formatters={"status": status_formatter},
    column_sortable_list=["created", "updated"],
    form_columns=[
        "status",
        "publish_date",
        "expire_date",
        "meta_title",
        "meta_description",
        "keywords",
        "should_auto_generate",
        "show_in_menu",
    ],
    form_excluded_columns=[
        "site",
        "created",
        "updated",
        "versions",
        "author",
        "last_edited_by",
    ],
    form_extra_fields={
        "status": SelectField(
            label=lazy_gettext("Status"), choices=Displayable.STATUS_CHOICES
        ),
        "slug": StringField(
            label=lazy_gettext("Slug"),
            description=lazy_gettext(
                "A user-friendly identifier used as a part of the URL."
            ),
        ),
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


class DisplayableAdmin(OyModelView):
    """Base ModelAdmin for Displayable."""

    def __init_subclass__(cls):
        for key, value in DISPLAYABEL_DEFAULTS.items():
            if getattr(cls, key, None) is None:
                setattr(cls, key, value)
        if not getattr(cls, "column_extra_row_actions", None):
            row_actions = list(default_row_actions)
            crowactions = getattr(cls, "column_extra_row_actions", None) or []
            if hasattr(cls, "get_preview_url"):
                crowactions.append(
                    LinkRowAction(
                        icon_class="fa fa-eye",
                        url=lambda v, i, r: cls.get_preview_url(r),
                        title=lazy_gettext("Preview in site"),
                    )
                )
            crowactions.extend(row_actions)
            setattr(cls, "column_extra_row_actions", crowactions)
        return cls

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
