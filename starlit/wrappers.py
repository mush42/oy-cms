# -*- coding: utf-8 -*-
"""	
    starlit.wrappers
    ~~~~~~~~~~

    Wrapps flask classes to provide the core functionality of
    the CMS engine

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import types
import sys
import os
from itertools import chain
from importlib import import_module
from warnings import warn
from collections import namedtuple

from werkzeug import import_string
from werkzeug.utils import cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, Blueprint
from flask.config import Config
from flask.helpers import locked_cached_property, get_root_path

from starlit.helpers import find_modules, import_modules
from starlit.fixtures import Fixtured


class AbstractField(object):
    """The field interface"""

    def __init__(self, name, type, label='',
            description=None, required=False,
            choices=None, default=None, **field_options):
        kwargs = locals()
        kwargs.pop('self')
        self.__dict__.update(kwargs)
        if self.default is not None:
            self.default = self.parse_default_value(kwargs['default'])
        if self.choices is not None:
            self.choices = self.parse_choices(kwargs['choices'])

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


class SingleSettingContainer(AbstractField):
    """A setting container that sets necessary defaults."""
    def __init__(self, raw_field):
        super().__init__(**raw_field)
        self.raw_field = raw_field
        if 'name' not in raw_field or 'type' not in raw_field:
            raise ValueError("'name' or 'type' are required in field definition "
                "for setting {} in module {}"
                .format(provided, mod.import_name)
            )
        if 'category' not in raw_field or not getattr(self, 'category', ''):
            self.category = 'general'


class StarlitConfig(Config):
    """Custom config class used by :class:`Starlit`"""
    
    def from_module_defaults(self, root_path):
        """Helper method to import the default config module from
        the given path.

        This method is called by :class:`Starlit` to load registered modules
        default configurations, which is represented by the presence of
        a module named **defaults.py** within the same directory of the
        module.

    .. Note:: Fall Back Configurations

        The configurations keys registered with this function are fall back
        values. This means a certain key will not be added if a
        config key with the same name already exists.

        :param root_path: The root path of the module
        """
        filename = os.path.join(root_path, 'defaults.py')
        d = types.ModuleType('default_config')
        d.__file__ = filename
        try:
            with open(filename, mode='rb') as config_file:
                exec(compile(config_file.read(), filename, 'exec'), d.__dict__)
        except IOError:
            return
        for key in dir(d):
            if key not in self and key.isupper():
                self[key] = getattr(d, key)


class StarlitModule(Blueprint, Fixtured):
    """StarlitModule is a :class:`flask.Blueprint` with some extras
    
    This class adds the ability to register editable settings which can be safely edited by the user during runtime.

    Basically  you can initialize it like other flask blueprints
    """
    
    def __init__(self, name, import_name, **kwargs):
        self.name = name
        self.import_name = import_name
        # flask wouldn't serve static files if this is not set 
        if not getattr(self, 'static_url_path', None):
            self.static_url_path="/static/" + self.name
        super(StarlitModule, self).__init__(
            self.name,
            self.import_name,
            static_url_path=self.static_url_path,
           **kwargs)
        self.settings_providers = []

    def register(self, app, *args, **kwargs):
        super(StarlitModule, self).register(app, *args, **kwargs)
        # Update the app.config with our defaults
        app.config.from_module_defaults(self.root_path)

    def settings_provider(self, func):
        """Record a function as a setting provider

        Setting provider functions should return a list of dicts.
        """
        self.settings_providers.append(func)
        def wrapped(*a, **kw):
            return func(*a, **kw)
        return wrapped

    def get_provided_settings(self):
        """
        Iterate over registered settings providers
        and return settings.
        """
        for provider in self.settings_providers:
            yield provider(self)


class Starlit(Flask):
    """Wrapps the :class:flask.Flask` to provide additional functionality.
    
    It add the following features:
        - Custom module system
        - Editable settings which are persisted to the database
    """
    
    # Custom configuration class :class:`StarlitConfig`
    config_class = StarlitConfig

    def __init__(self, *args, **kwargs):
        super(Starlit, self).__init__(*args, **kwargs)
        self.modules = {}
        self._provided_settings = None

    @locked_cached_property
    def jinja_loader(self):
        """Templates provided by starlit modules should have higher priority"""
        mod_templates = [
            FileSystemLoader(self.template_folder),
            super(Starlit, self).jinja_loader,
        ]
        for mod in self.modules.values():
            if mod.template_folder:
                templates_dir = os.path.join(get_root_path(mod.import_name), mod.template_folder)
                mod_templates.append(FileSystemLoader(templates_dir))
        return ChoiceLoader(mod_templates)

    def register_module(self, module, **options):
        """Register a starlit module with this application"""
        super(Starlit, self).register_blueprint(blueprint=module, **options)
        self.modules[module.name] = module

    def find_starlit_modules(self, pkg):
        """Find all starlit modules within a given package.
        
        :param pkg: the dotted import_name of the package
        """
        for module in import_modules(pkg):
            modname = module.__name__
            if modname in self.config['EXCLUDED_MODULES']:
                continue
            starlit_modules = (
              v for v in module.__dict__.values()
              if isinstance(v, StarlitModule)
            )
            for mod in set(starlit_modules):
                yield mod

    def _collect_provided_settings(self):
        for mod in self.modules.values():
            for provided in chain.from_iterable(mod.get_provided_settings()):
                self._provided_settings.setdefault(
                  mod.name, []).append(
                  SingleSettingContainer(provided)
                )

    @property
    def provided_settings(self):
        """Iterate over registered modules to collect editable settings"""
        if self._provided_settings is None:
            self._provided_settings = {}
            self._collect_provided_settings()
        yield from self._provided_settings.items()
