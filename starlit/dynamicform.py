# -*- coding: utf-8 -*-
"""	
    starlit.dynamicform
    ~~~~~~~~~~

    A form that can construct its fields from
    a list of dicts containing fields data

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import dataclasses
from collections import UserString, OrderedDict, namedtuple
from typing import Callable, Any, Iterable, Tuple, Dict, ClassVar, Union
from flask import current_app
from flask_wtf import FlaskForm
from starlit.babel import lazy_gettext
from starlit.signals import starlit_app_starting
from wtforms import Form as wtForm, ValidationError
from wtforms.fields import (
    Field as WTField,
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

Validator = Callable[[wtForm, WTField], None]


@dataclasses.dataclass(frozen=True)
class FieldType:
    name: str
    display_name: str
    field: WTField
    validators: Tuple[Validator] = ()


default_field_types = (
    FieldType("text", lazy_gettext("Single line text input"), StringField),
    FieldType("number", lazy_gettext("Number input"), IntegerField),
    FieldType("select", lazy_gettext("Select Box"), SelectField),
    FieldType("checkbox", lazy_gettext("Check Box"), BooleanField),
    FieldType("radio", lazy_gettext("Radio List"), RadioField),
    FieldType("textarea", lazy_gettext("Multi-line text input"), TextAreaField),
    FieldType("email", lazy_gettext("Email Input"), EmailField, (email(),)),
    FieldType("date", lazy_gettext("Date input"), DateField),
    FieldType("datetime", lazy_gettext("Date & Time input"), DateTimeField),
    FieldType("url", lazy_gettext("URL input"), URLField, (url(),)),
    FieldType("tell", lazy_gettext("Tell input"), TelField),
    FieldType("file", lazy_gettext("File input"), FileField),
)


@dataclasses.dataclass
class Field:
    name: str
    type: str
    label: str = ""
    description: str = ""
    required: bool = False
    default: Union[Any, Callable[["Field"], Any]] = None
    choices: Union[Iterable[str], Callable[["Field"], Iterable[str]], Dict[str, str], None] = None
    options: Dict = dataclasses.field(default_factory=dict)

    def __post_init__(self):
        if not self.description:
            self.description = ""
        if self.default and callable(self.default):
            self.default = self.default(self)
        if self.choices is not None:
            if callable(self.choices):
                self.choices = self.choices(self)
            if type(self.choices) is dict:
                self.choices = self.choices.items()
                return
            elif type(self.choices) is not str:
                raise TypeError("{} Invalid value for field choices.".format(choices))
            rv = []
            for choice in self.choices.split(";"):
                rv.append(choice.split(":"))
            self.choices = rv

    def to_wtf(self):
        field_types = current_app.available_field_types
        metadata = field_types.get(self.type, None)
        if metadata is None:
            raise NotSupportedFieldTypeError(
                f"{self.type} is not a supported field type."
            )
        ConcreteField = metadata.field
        kwargs = {}
        kwargs["validators"] = list(metadata.validators)
        kwargs["render_kw"] = {}
        kwargs['label'] = self.label
        kwargs['description'] = self.description
        kwargs['default'] = self.default
        if self.choices is not None:
            kwargs['choices'] = self.choices
        if self.required:
            kwargs["validators"].append(data_required())
            kwargs["render_kw"]["required"] = True
        if "length" in self.options:
            max_length = self.options["length"]
            kwargs["validators"].append(length(max=max_length))
            kwargs["render_kw"]["aria-max"] = max_length
        if "render_kw" in self.options:
            kwargs["render_kw"].update(self.options.pop("render_kw"))
        kwargs.update(self.options)
        return self.name, ConcreteField, kwargs


class NotSupportedFieldTypeError(Exception):
    """Raised during the construction of the field"""


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

    @staticmethod
    def normalize(fieldset):
        fields = []
        for field in fieldset:
            if isinstance(field, Field):
                fields.append(field)
            elif type(field) is dict:
                fields.append(Field(**field))
            else:
                fields.append(Field(
                    name=field.name,
                    type=field.type,
                    label=field.label,
                    description=field.description,
                    required=field.required,
                    default=field.default,
                    choices=field.choices
                ))
        return fields

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
            fieldname, concrete_field, kwargs = field.to_wtf()
            if fields_only:
                self.unbound_fields.append((fieldname, concrete_field(**kwargs)))
            else:
                setattr(self.raw_form, fieldname, concrete_field(**kwargs))
        self._generated = True


@starlit_app_starting.connect
def _prepare_fields(app):
    field_types = list(default_field_types)
    if "EXTRA_FIELD_TYPES" in app.config:
        field_types.extend(app.config["EXTRA_FIELD_TYPES"])
    app.available_field_types = OrderedDict((ftype.name, ftype) for ftype in field_types)
