from collections import namedtuple
from flask_wtf import FlaskForm
from starlit.babel import lazy_gettext
from wtforms.fields import (
    StringField, SelectField, RadioField,
    BooleanField, TextAreaField, FileField
)
from wtforms.fields.html5 import (
    IntegerField, DateField, DateTimeField,
    EmailField, TelField, URLField,
)
from wtforms.validators import (
    data_required, email,
    length, url, 
) 
from flask_admin.contrib.sqla.fields import QuerySelectField
from starlit.util.wtf import FileSelectorField, RichTextAreaField
from starlit.util.option import Option

info = namedtuple('info', 'name field')

FIELD_MAP = dict(
    text=info(lazy_gettext('Single line text input'), StringField),
    number=info(lazy_gettext('Number input'), IntegerField),
    select=info(lazy_gettext('Select Box'), SelectField),
    checkbox=info(lazy_gettext('Check Box'), BooleanField),
    radio=info(lazy_gettext('Radio List'), RadioField),
    textarea=info(lazy_gettext('Multi-line text input'), TextAreaField),
    email=info(lazy_gettext('Email Input'), EmailField),
    date=info(lazy_gettext('Date input'), DateField),
    datetime=info(lazy_gettext('Date & Time input'), DateTimeField),
    url=info(lazy_gettext('URL input'), URLField),
    tel=info(lazy_gettext('Tell input'), TelField),
    file_input=info(lazy_gettext('File input'), FileField)
)

# Those fields are only available for admin users or staff.
ADMIN_FIELD_MAP = dict(FIELD_MAP)
ADMIN_FIELD_MAP.update({
    'file_selector': info(lazy_gettext('File Selector'), FileSelectorField),
    'wysiwyg': info(lazy_gettext('WYSIWYG Editor'), RichTextAreaField),
    'select2': info(lazy_gettext('Select2 Field'), QuerySelectField),
})

VALIDATORS_MAP = {
    #EmailField: email(),
    #URLField: url(),
}

class DynamicForm(object):
    """
    A Dynamic form generator.
    Jus pass a list of objects implementing some sort of
    field-interface, Which is basicly providing a label, type, and description and
    sevral other optional attributes.
    You can access the scafolded form using the form property
    and the generated unbound fields using the field property
    """
    def __init__(self, fields, base_form=FlaskForm, with_admin=False):
        class FormWithDynamiclyGeneratedFields(base_form):
            pass
        self.raw_form = FormWithDynamiclyGeneratedFields
        self.raw_fields = self.normalize(fields)
        self.unbound_fields = list()
        self.field_map = FIELD_MAP if not with_admin else ADMIN_FIELD_MAP
        self._generated = False

    def normalize(self, fields):
        rv = list()
        for field in fields:
            if hasattr(field, 'keys'):
                rv.append(Option(**field))
            else:
                rv.append(field)
        return rv

    @property
    def form(self):
        if not self._generated:
            self.generate_fields()
        return self.raw_form()

    @property
    def fields(self):
        if not self._generated:
            self.generate_fields(fields_only=True)
        return self.unbound_fields

    def generate_fields(self, fields_only=False):
        for field in self.raw_fields:
            field_info = self.field_map.get(field.type)
            if field_info is None:
                raise TypeError('Field type %s is not supported' %field.type)
            Field = field_info.field
            kwargs = dict()
            kwargs['label'] = field.label
            kwargs['description'] = field.description or ''
            kwargs['default'] = self.parse_default(field.type, field.default)
            kwargs['validators'] = []
            kwargs['render_kw'] = {}
            if getattr(field, 'field_options', None) is not None:
                kwargs['render_kw'].update(field.field_options.get('render_kw', {}))
            if field.type == 'select' or field.type == 'radio':
                kwargs['choices'] = self.parse_choices(field.choices)
            if getattr(field, 'required', False):
                kwargs['validators'].append(data_required())
                kwargs['render_kw']['required'] = True
            if VALIDATORS_MAP.get(Field):
                kwargs['validators'].append(VALIDATORS_MAP[Field])
            if hasattr(field, 'length'):
                max_length = field.length or -1
                kwargs['validators'].append(length(max=max_length))
                kwargs['render_kw']['aria-max'] = max_length
            kwargs.update((getattr(field, 'field_options', None) or {}))
            if fields_only:
                self.unbound_fields.append((field.name, Field(**kwargs)))
            else:
                setattr(self.raw_form, field.name, Field(**kwargs))
        self._generated = True

    def parse_default(self, field_type, value):
        if value is None:
            return
        elif callable(value):
            value = value()
        if field_type == 'checkbox':
            if type(value) is bool:
                return value
            elif value.lower() in ['true', 'yes', 'on', 'ok']:
                return True
            else:
                return False
        return value

    def parse_choices(self, choices):
        if callable(choices):
            choices = choices()
        if hasattr(choices, 'keys'):
            return choices.items()
        elif type(choices) is not str:
            return choices
        rv = []
        for choice in choices.split(';'):
            rv.append(choice.split(':'))
        return rv
