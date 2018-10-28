from collections import namedtuple
from flask_wtf import FlaskForm
from starlit.babel import lazy_gettext
from wtforms.fields import (
    StringField,
    SelectField,
    RadioField,
    BooleanField,
    TextAreaField,
    FileField,
)
from wtforms.fields.html5 import (
    IntegerField,
    DateField,
    DateTimeField,
    EmailField,
    TelField,
    URLField,
)
from wtforms.validators import data_required, email, length, url
from starlit.wrappers import AbstractField


info = namedtuple("info", "name field")

FIELD_MAP = dict(
    text=info(lazy_gettext("Single line text input"), StringField),
    number=info(lazy_gettext("Number input"), IntegerField),
    select=info(lazy_gettext("Select Box"), SelectField),
    checkbox=info(lazy_gettext("Check Box"), BooleanField),
    radio=info(lazy_gettext("Radio List"), RadioField),
    textarea=info(lazy_gettext("Multi-line text input"), TextAreaField),
    email=info(lazy_gettext("Email Input"), EmailField),
    date=info(lazy_gettext("Date input"), DateField),
    datetime=info(lazy_gettext("Date & Time input"), DateTimeField),
    url=info(lazy_gettext("URL input"), URLField),
    tel=info(lazy_gettext("Tell input"), TelField),
    file=info(lazy_gettext("File input"), FileField),
)

VALIDATORS_MAP = {
    # EmailField: email(),
    # URLField: url(),
}


class NotSupportedFieldTypeError(Exception):
    """Raised during the construction of the field"""


def make_concrete_field(field, field_map=FIELD_MAP, validators=VALIDATORS_MAP):
    metadata = field_map.get(field.type, None)
    if metadata is None:
        raise NotSupportedFieldTypeError(
            "{} is not a supported field type.".format(field.type)
        )
    ConcreteField = metadata.field
    kwargs = dict()
    kwargs["label"] = field.label
    kwargs["description"] = field.description or ""
    kwargs["default"] = field.default
    kwargs["validators"] = []
    kwargs["render_kw"] = {}
    if field.type in ("select", "radio"):
        kwargs["choices"] = field.choices
    if getattr(field, "required", False):
        kwargs["validators"].append(data_required())
        kwargs["render_kw"]["required"] = True
    if ConcreteField in validators:
        kwargs["validators"].extend(validators[ConcreteField])
    if hasattr(field, "length"):
        max_length = field.length or -1
        kwargs["validators"].append(length(max=max_length))
        kwargs["render_kw"]["aria-max"] = max_length
    if (field.field_options is not None) and ("render_kw" in field.field_options):
        kwargs["render_kw"].update(field.field_options.pop("render_kw", {}))
        kwargs.update(field.field_options)
    return field.name, ConcreteField, kwargs


class DynamicForm(object):
    """
    A Dynamic form generator:

    The simplest use is to pass an iterable of dicts
    containing some metadata about the fields you want
    to create.
    
    Metadata should contain at least name and type and
    optionally description and several other attributes.
    
    You can access the scaffolded form using the form property
    and the generated unbound fields using the field property
    """

    def __init__(self, fieldset, base_form=FlaskForm):
        class FormWithDynamiclyGeneratedFields(base_form):
            pass

        self.raw_form = FormWithDynamiclyGeneratedFields
        self.fieldset = self.normalize(fieldset)
        self.unbound_fields = list()
        self._generated = False

    def normalize(self, fields):
        for field in fields:
            if type(field) is dict:
                yield AbstractField(**field)
            yield field

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
        for field in self.fieldset:
            fieldname, concrete_field, kwargs = make_concrete_field(field)
            if fields_only:
                self.unbound_fields.append((fieldname, concrete_field(**kwargs)))
            else:
                setattr(self.raw_form, fieldname, concrete_field(**kwargs))
        self._generated = True
