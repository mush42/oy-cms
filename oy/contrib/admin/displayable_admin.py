from flask import flash, abort
from flask_admin import expose
from flask_admin.model import typefmt
from flask_admin.model.template import EndpointLinkRowAction
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


class DisplayableAdmin(OyModelView):
    """Base ModelAdmin for Displayable."""

    def __init_subclass__(cls):
        for key, value in DISPLAYABEL_DEFAULTS.items():
            if getattr(cls, key, None) is None:
                setattr(cls, key, value)
        return cls
