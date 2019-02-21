# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.polymorphic_prop
    ~~~~~~~~~~

    Provides helper mixin classes for special sqlalchemy models

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import sqlalchemy.types as types
from sqlalchemy import literal_column, event
from sqlalchemy.orm.interfaces import PropComparator
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.declarative import declared_attr
from werkzeug.datastructures import FileStorage
from depot.fields.sqlalchemy import UploadedFileField
from depot.io.utils import FileIntent
from oy.boot.sqla import db


class ProxiedDictMixin(object):
    """Adds obj[key] access to a mapped class.

    This class basically proxies dictionary access to an attribute
    called ``_proxied``.  The class which inherits this class
    should have an attribute called ``_proxied`` which points to a dictionary.
    """

    def __len__(self):
        return len(self._proxied)

    def __iter__(self):
        return iter(self._proxied)

    def __getitem__(self, key):
        return self._proxied[key]

    def __contains__(self, key):
        return key in self._proxied

    def get(self, key):
        return self._proxied.get(key)

    def __setitem__(self, key, value):
        self._proxied[key] = value

    def __delitem__(self, key):
        del self._proxied[key]


class ReadOnlyProxiedDictMixin(ProxiedDictMixin):
    """Like :class:`ProxiedDictMixin` but disables the addition of
    new keys and deletion of existing ones
    """

    def __setitem__(self, key, value):
        if key not in self._proxied:
            raise AttributeError("Cann't Set Attribute")
        self._proxied[key] = value

    def __delitem__(self, key):
        raise AttributeError("Deleting is not allowed")


class PolymorphicVerticalProperty(object):
    """A key/value pair with polymorphic value storage.

    The class which is mapped should indicate typing information
    within the "info" dictionary of mapped Column objects.
    """

    def __init__(self, key=None, value=None):
        self.key = key
        self.value = value

    @hybrid_property
    def value(self):
        fieldname, discriminator = self.type_map[self.type]
        if fieldname is None:
            return None
        else:
            return getattr(self, fieldname)

    @value.setter
    def value(self, value):
        py_type = type(value)
        fieldname, discriminator = self.type_map[py_type]

        self.type = discriminator
        if fieldname is not None:
            setattr(self, fieldname, value)

    @value.deleter
    def value(self):
        self._set_value(None)

    @value.comparator
    class value(PropComparator):
        """A comparator for .value, builds a polymorphic comparison via CASE.

        """

        def __init__(self, cls):
            self.cls = cls

        def _case(self):
            pairs = set(self.cls.type_map.values())
            whens = [
                (
                    literal_column("'%s'" % discriminator),
                    cast(getattr(self.cls, attribute), String),
                )
                for attribute, discriminator in pairs
                if attribute is not None
            ]
            return case(whens, self.cls.type, null())

        def __eq__(self, other):
            return self._case() == cast(other, String)

        def __ne__(self, other):
            return self._case() != cast(other, String)

    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.value)


@event.listens_for(PolymorphicVerticalProperty, "mapper_configured", propagate=True)
def on_new_class(mapper, cls_):
    """Look for Column objects with type info in them, and work up
    a lookup table."""
    info_dict = {}
    info_dict[type(None)] = (None, "none")
    info_dict["none"] = (None, "none")
    for k in mapper.c.keys():
        col = mapper.c[k]
        if "type" in col.info:
            python_type, discriminator = col.info["type"]
            if type(python_type) in (list, tuple):
                for pty in python_type:
                    info_dict[pty] = (k, discriminator)
            else:
                info_dict[python_type] = (k, discriminator)
            info_dict[discriminator] = (k, discriminator)
    cls_.type_map = info_dict


class DynamicProp(PolymorphicVerticalProperty):
    key = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64))
    int_value = db.Column(db.Integer, info={"type": (int, "integer")})
    str_value = db.Column(db.Unicode(5120), info={"type": (str, "string")})
    bool_value = db.Column(db.Boolean, info={"type": (bool, "boolean")})


class DynamicPropWithFile(DynamicProp):

    @declared_attr
    def file_value(cls):
        kwargs = getattr(cls, "__file_field_args__", {})
        nullable = kwargs.pop("nullable", True)
        info = kwargs.pop("info", {})
        info["type"] = ((FileIntent, FileStorage), "file")
        return db.Column(
            UploadedFileField(**kwargs),
            nullable=nullable,
            info=info
        )
