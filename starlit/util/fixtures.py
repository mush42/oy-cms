import os
import json
from dateutil.parser import parse
from werkzeug import import_string
from werkzeug.utils import cached_property
from starlit.exceptions import BadlyFormattedFixture
from starlit.boot.exts.sqla import db


class _Fixtured(object):
    """An object that is able to install fixtures from its module path."""
    
    def deserialize_instances(self, model_name, objs):
        """Given a dictionary of the form {'model_import_path': [objs...]}
        this will return an instance of model with each obj of objs as kwargs
        """
        model = import_string(model_name)
        for obj in objs:
            for k, v in obj.items():
                if hasattr(v, 'strip') and v.startswith('_file'):
                    to_read = os.path.join(self.root_path, 'fixtures', '_files', v.lstrip('_file:'))
                    obj[k] = open(to_read, 'r').read()
                elif 'date' in k:
                        obj[k] = parse(v)
            yield model(**obj)

    @cached_property
    def fixtures(self):
        """Returns the json decoded fixture or None"""
        try:
            with self.open_resource('fixtures/data.json') as datafile:
                return json.load(datafile)
        except IOError:
            return
        except json.JSONDecodeError:
            raise BadlyFormattedFixture("Error deserializing fixtures for: " + self.module)

    def install_fixtures(self):
        if not self.fixtures:
            return
        for model_import_path, objs in self.fixtures.items():
            for instance in self.deserialize_instances(model_import_path, objs):
                db.session.add(instance)
                db.session.commit()
            yield model_import_path