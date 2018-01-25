import csv
from flask import Response, stream_with_context
from flask_admin import expose
from flask_admin.model.template import EndpointLinkRowAction
from flask_admin.model.form import InlineFormAdmin
from flask_admin import helpers as h
from flask_admin._compat import csv_encode
from flask_wtf import Form
from werkzeug import secure_filename
from wtforms_alchemy import ModelForm
from wtforms.fields import IntegerField, SelectField
from wtforms.widgets import HiddenInput

from starlit.boot.exts.sqla import db
from starlit.boot.exts.admin import admin, AuthenticationViewMixin

from starlit.modules.page.admin import PageAdmin
from starlit.babel import lazy_gettext
from starlit.util.wtf import RichTextAreaField
from starlit.util.helpers import date_stamp
from .models import Form, Field


class FormAdmin(PageAdmin):
    inline_models = [(Field, dict(
            form_columns=['id', 'name', 'label', 'description', 'type', 'choices', 'default', 'required', 'max_length'],
                form_extra_fields={'type': SelectField(label=Field.type.info['label'], description=Field.type.info['description'], choices=sorted(Field.type.info['choices']))}
            ),),]
    column_extra_row_actions = list(PageAdmin.column_extra_row_actions)
    column_extra_row_actions.append(EndpointLinkRowAction(icon_class='fa fa-download', endpoint='.export_entries', title=lazy_gettext('Export Entries as CSV'), id_arg='pk'))
    form_excluded_columns = ["children", "contenttype", "slug_path"]
    form_rules = list(PageAdmin.form_rules)
    form_rules.insert(6, 'fields')
    form_rules.insert(7, 'submit_text')
    form_rules.insert(8, 'submit_message')
    form_overrides = dict(PageAdmin.form_overrides)
    form_overrides.update({
        'submit_message': RichTextAreaField,
    })

    @expose('/export-entries/<int:pk>')
    def export_entries(self, pk):
        """Taken from Flask-Admin with some modifications, no shame!"""
        form = self.get_one(str(pk))
        filename = "attachment; filename=%s.csv" %("%s-%s" %(form.slug, date_stamp(form.updated)))
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
            titles = [csv_encode('date')] + [csv_encode(field.name) for field in form.fields]
            yield writer.writerow(titles)
            for entry in form.entries:
                vals = [csv_encode(entry.created.isoformat())] + [csv_encode(field.value) for field in entry.fields]
                yield writer.writerow(vals)
        return Response(
            stream_with_context(generate()),
            headers={'Content-Disposition': filename},
            mimetype='text/csv'
        )

admin.add_view(FormAdmin(Form, db.session, name=lazy_gettext('Form'), category=lazy_gettext('Pages')))