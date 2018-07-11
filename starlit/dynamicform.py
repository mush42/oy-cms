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
    file_input=info(lazy_gettext('File input'), FileField),
)

VALIDATORS_MAP = {
    #EmailField: email(),
    #URLField: url(),
}


class NotSupportedFieldTypeError(Exception):
    """Raised during the construction of the field"""


class FieldBlueprint:
    """A bluprint to construct a form field."""

    def __init__(self, dyform, name, type, label='',
            description=None, required=False,
            choices=None, default=None, **field_options):
        kwargs = locals()
        try:
            self.metadata = dyform.field_map[kwargs['type']]
        except KeyError:
            raise NotSupportedFieldTypeError(
                "{} is not a supported field type."
                .format(self.type)
                )
        kwargs.pop('self')
        if 'default' in kwargs:
            kwargs['default'] = self.parse_default_value(kwargs.pop('default'))
        if 'choices' in kwargs:
            kwargs['choices'] = self.parse_choices(kwargs.pop('choices'))
        self.__dict__.update(kwargs)

    def make_concrete(self):
        ConcreteField = self.metadata.field
        kwargs = dict()
        kwargs['label'] = self.label
        kwargs['description'] = self.description or ''
        kwargs['default'] = self.default
        kwargs['validators'] = []
        kwargs['render_kw'] = {}
        if self.field_options and 'render_kw' in self.field_options:
            kwargs['render_kw'].update(self.field_options.pop('render_kw', {}))
        if self.type in ('select', 'radio'):
            kwargs['choices'] = self.choices
        if getattr(self, 'required', False):
            kwargs['validators'].append(data_required())
            kwargs['render_kw']['required'] = True
        if ConcreteField in self.dyform.validattor_map:
            kwargs['validators'].append(self.dyform.validattor_map[ConcreteField])
        if hasattr(self, 'length'):
            max_length = field.length or -1
            kwargs['validators'].append(length(max=max_length))
            kwargs['render_kw']['aria-max'] = max_length
        kwargs.update(self.field_options)
        return ConcreteField, kwargs

    def parse_default_value(self, value):
        if value is None:
            return
        elif callable(value):
             value = value(self)
        if self.type == 'checkbox' and type(value) is not bool:
            raise TypeError("Invalid default value for checkbox")
        return value


    def parse_choices(self, choices):
        if callable(choices):
            choices = choices(self)
        if hasattr(choices, 'keys'):
            return choices.items()
        elif type(choices) is not str:
            raise TypeError("{} Invalid value for field choices.". format(choices))
        for choice in choices.split(';'):
            yield choice.split(':')


class DynamicForm(object):
    """
    A Dynamic form generator:

    Just pass an iterable of dicts containing some
    metadataabout the fields you want to create.
    
    Metadata should contain at least name and type and
    optionally description and several other attributes.
    
    You can access the scaffolded form using the form property
    and the generated unbound fields using the field property
    """
    # A list of field info from which to start
    field_map = FIELD_MAP
    # A list of validattors
    validattor_map = VALIDATORS_MAP

    def __init__(self, fields, base_form=FlaskForm):
        class FormWithDynamiclyGeneratedFields(base_form):
            pass
        self.raw_form = FormWithDynamiclyGeneratedFields
        self.fields = self.normalize(fields)
        self.unbound_fields = list()
        self._generated = False

    def normalize(self, fields):
        for field in fields:
            yield FieldBlueprint(self, **field) if hasattr(field, 'keys') else field

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
        for field in self.fields:
            concrete_field, kwargs = field.make_concrete()
            if fields_only:
                self.unbound_fields.append((field.name, concrete_field(**kwargs)))
            else:
                setattr(self.raw_form, field.name, concrete_field(**kwargs))
        self._generated = True

