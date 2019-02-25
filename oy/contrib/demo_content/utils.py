import os
import json
from contextlib import suppress
from dateutil.parser import parse
from sqlalchemy.exc import IntegrityError
from werkzeug import import_string
from werkzeug.utils import cached_property
from oy.exceptions import OyException
from oy.boot.sqla import db


def deserialize_instance(module, model, **attrs):
    """Given a model and attrs as a dict of keyword args
    this will return an instance of model with the fields
    """
    for k, v in attrs.items():
        if type(v) is str and v.startswith("__files__"):
            to_read = os.path.join(module.root_path, "fixtures", "__files__", v[10:])
            attrs[k] = open(to_read, "r").read()
        elif "date" in k:
            attrs[k] = parse(v)
    return model(**attrs)


class BadlyFormattedFixture(OyException):
    """Raised when a fixture could not be decoded"""


class FixtureInstaller:
    """A utility class to install fixtures from modules."""

    def __init__(self, module):
        self.module = module

    @cached_property
    def fixtures(self):
        """Returns the json decoded fixture or None"""
        try:
            with suppress(IOError):
                with self.module.open_resource("fixtures/data.json") as datafile:
                    return json.load(datafile)
        except json.JSONDecodeError:
            raise BadlyFormattedFixture(
                f"Error deserializing fixtures for:  {self.module.name}."
            )

    def install(self):
        if not self.fixtures:
            return
        deserializer = deserialize_instance
        for model_import_path, objs in self.fixtures.items():
            model = import_string(model_import_path)
            if hasattr(model, "deserialize_instance"):
                deserializer = model.deserialize_instance
            for obj in objs:
                instance = deserializer(self.module, model, **obj)
                db.session.add(instance)
                try:
                    db.session.commit()
                except IntegrityError:
                    # Most likely we have a simular row in db
                    db.session.rollback()
                    continue
