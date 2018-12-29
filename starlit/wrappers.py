# -*- coding: utf-8 -*-
"""	
    starlit.wrappers
    ~~~~~~~~~~

    Wrapps flask classes to provide the core functionality of
    the CMS engine

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

import sys
import os
import json
from typing import Iterable
from itertools import chain
from importlib import import_module
from warnings import warn
from collections import UserString, OrderedDict

from werkzeug import import_string
from werkzeug.utils import cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, Blueprint
from flask.config import Config
from flask.helpers import locked_cached_property, get_root_path

from starlit.content_renderer import ContentRendererMixin
from starlit.helpers import exec_module, find_modules, import_modules
from starlit.fixtures import Fixtured
from starlit.signals import starlit_module_registered, starlit_app_starting


class DualValueString(UserString):
    """A string that has two values:
          - a primary value: str
          - a dictionary containing extra values
    """

    def __init__(self, seq, **extra):
        super(DualValueString, self).__init__(seq)
        self.args = extra

    def __str__(self):
        return self.data

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
        filename = os.path.join(root_path, "defaults.py")
        if not os.path.isfile(filename):
            return
        d = exec_module(filename, "default_module_config")
        for key in dir(d):
            if key not in self and key.isupper():
                self[key] = getattr(d, key)


class StarlitModule(Blueprint, Fixtured):
    """StarlitModule is a :class:`flask.Blueprint` with some extras
    
    This class adds the ability to register editable settings which can be safely
    edited by the user during runtime.

    Basically  you can initialize it like other flask blueprints
    """

    def __init__(
        self, name, import_name, viewable_name=None, **kwargs
    ):
        # flask wouldn't serve static files if static_url_path is not set
        auto_static_url_path = kwargs.get(
            "static_url_path", None
        ) or "/static/" + name.replace(".", "-")
        self.viewable_name = viewable_name
        # A list of dicts or functions that return a list of dicts
        self.settings = []
        self.__module__ = import_name
        super(StarlitModule, self).__init__(
            name, import_name, static_url_path=auto_static_url_path, **kwargs
        )

    def register(self, app, *args, **kwargs):
        super(StarlitModule, self).register(app, *args, **kwargs)
        # Update the app.config with our defaults
        app.config.from_module_defaults(self.root_path)
        starlit_module_registered.send(app, module=self)

    def settings_provider(self, category=None):
        """Record a function as a setting provider

        Setting provider functions should return a list of dicts.
        """

        def decorator(func):
            func.category = category or self.name
            self.settings.append(func)
            return func

        return decorator


class Starlit(Flask, ContentRendererMixin):
    """Wrapps the :class:flask.Flask` to provide additional functionality.
    
    It add the following features:
        - Custom module system
        - Editable settings which are persisted to the database
    """

    # Custom configuration class :class:`StarlitConfig`
    config_class = StarlitConfig

    def __init__(self, *args, **kwargs):
        super(Starlit, self).__init__(*args, **kwargs)
        ContentRendererMixin.__init__(self)
        self.before_first_request_funcs.append(
            lambda: starlit_app_starting.send(self)
        )
        self.provided_settings_dict = None
        self.modules = OrderedDict()
        # Holds variable data which is useful for this app instance.
        self.data = {}


    @locked_cached_property
    def jinja_loader(self):
        """Templates provided by starlit modules should have higher priority"""
        mod_templates = []
        for mod in self.modules.values():
            if mod.template_folder:
                mod_templates.append(mod.jinja_loader)
        # Recently registered modules have higher priority
        mod_templates.reverse()

        mod_templates.append(super(Starlit, self).jinja_loader)
        return ChoiceLoader(tuple(mod_templates))

    def register_module(self, module, **options):
        """Register a starlit module with this application"""
        super(Starlit, self).register_blueprint(blueprint=module, **options)
        self.modules[module.name] = module
        # Force-refresh provided settings
        self.provided_settings_dict = None

    def find_starlit_modules(self, pkg):
        """Find all starlit modules within a given package.
        
        :param pkg: the dotted import_name of the package
        """
        for module in import_modules(pkg):
            modname = module.__name__
            if modname in self.config["EXCLUDED_MODULES"]:
                continue
            starlit_modules = (
                v for v in module.__dict__.values() if isinstance(v, StarlitModule)
            )
            for mod in set(starlit_modules):
                yield mod

    def _collect_provided_settings(self):
        self.provided_settings_dict = {}
        for mod in self.modules.values():
            for setting_func in mod.settings:
                cat = setting_func.category
                if cat not in self.modules:
                    raise LookupError(
                        f"'{cat}' is being used as a setting category\
                        in module {mod.name}, function {setting_func.__name__}\
                        but it is not a registered module."
                    )
                provided = setting_func(self)
                for setting in provided:
                    viewable_name = self.modules[cat].viewable_name
                    category = DualValueString(cat, viewable_name=viewable_name)
                    self.provided_settings_dict.setdefault(category, []).append(setting)

    @property
    def provided_settings(self):
        """Iterate over registered modules to collect editable settings"""
        if self.provided_settings_dict is None:
            self._collect_provided_settings()
        yield from self.provided_settings_dict.items()
