# -*- coding: utf-8 -*-
"""
    oy.contrib.form.admin
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the admin interface for editing oy forms.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import csv
from flask import current_app, request, Response, stream_with_context, render_template
from flask_admin import expose
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.model.form import InlineFormAdmin
from flask_admin import helpers as h
from flask_admin._compat import csv_encode
from flask_wtf import Form
from werkzeug import secure_filename
from wtforms.fields import IntegerField
from wtforms.widgets import HiddenInput
from wtforms_components import SelectField
from oy.models import db
from oy.babel import lazy_gettext
from oy.helpers import paginate_with_args
from oy.contrib.admin.wrappers import AuthenticationViewMixin
from oy.contrib.formfields import TinymceTextAreaField
from oy.contrib.admin.core.page import PageAdmin
from .models import Form, Field, FormEntry


def _process_field_value(field):
    """Used in the csv writing task to return an
    appropriate representation 
    """
    if field.value == "":
        return "[Empty]"
    if field.type == "boolean":
        return "True" if field.value else "False"
    return field.value


def _gen_csv_file_name(form):
    form_updated = form.updated.isoformat().replace(":", "-")
    return "-".join((request.host, form.slug, form_updated)) + ".csv"


def field_type_choices():
    return [
        (ft.name, ft.display_name)
        for ft in current_app.data["available_field_types"].values()
    ]


class FormAdmin(PageAdmin):

    column_extra_row_actions = list(PageAdmin.column_extra_row_actions)
    column_extra_row_actions += [
        EndpointLinkRowAction(
            icon_class="fa fa-download",
            endpoint=".export_entries",
            title=lazy_gettext("Export Entries as CSV"),
            id_arg="pk",
        ),
        EndpointLinkRowAction(
            icon_class="fa fa-table",
            endpoint=".view_entries",
            title=lazy_gettext("View Entries"),
            id_arg="pk",
        ),
    ]
    form_excluded_columns = list(PageAdmin.form_excluded_columns) + [
        "author",
        "created",
        "updated",
        "entries",
    ]
    form_columns = list(PageAdmin.form_columns)
    form_columns.insert(6, "fields")
    form_columns.insert(7, "submit_text")
    form_columns.insert(8, "submit_message")
    form_overrides = {"submit_message": TinymceTextAreaField}
    inline_models = [
        (
            Field,
            dict(
                form_columns=[
                    "id",
                    "name",
                    "label",
                    "description",
                    "type",
                    "choices",
                    "default",
                    "required",
                    "max_length",
                ],
                form_extra_fields={
                    "type": SelectField(
                        label=Field.type.info["label"],
                        description=Field.type.info["description"],
                        choices=field_type_choices,
                    )
                },
            ),
        )
    ]

    @expose("/export-entries/<int:pk>")
    def export_entries(self, pk):
        """Taken from Flask-Admin with some modifications, no shame!"""
        form = self.get_one(str(pk))
        filename = "attachment; filename=%s" % _gen_csv_file_name(form)

        class Echo(object):
            """
            An object that implements just the write method of the file-like
            interface.
            """

            def write(self, value):
                """
                Write the value by returning it, instead of storing
                in a buffer.
                """
                return value

        writer = csv.writer(Echo())

        def generate():
            # Append the column titles at the beginning
            titles = [csv_encode("date")] + [
                csv_encode(field.name) for field in form.fields
            ]
            yield writer.writerow(titles)
            for entry in form.entries:
                vals = [csv_encode(entry.created.isoformat())] + [
                    csv_encode(_process_field_value(field)) for field in entry.fields
                ]
                yield writer.writerow(vals)

        return Response(
            stream_with_context(generate()),
            headers={"Content-Disposition": filename},
            mimetype="text/csv",
        )

    @expose("/view-entries/<int:pk>")
    def view_entries(self, pk):
        """View form entries"""
        form = self.get_one(str(pk))
        entries = FormEntry.query.filter_by(form=form)
        paginator = paginate_with_args(entries)
        return self.render(
            "oy_admin/form-entries.html",
            form=form,
            paginator=paginator,
            val_proc=_process_field_value,
        )


def register_admin(app, admin):
    admin.add_view(
        FormAdmin(
            Form,
            db.session,
            name=lazy_gettext("Forms"),
            menu_icon_type="fa",
            menu_icon_value="fa-wpforms",
        )
    )
