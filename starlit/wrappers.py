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
from importlib import import_module
from warnings import warn
from collections import namedtuple

from werkzeug import import_string
from werkzeug.utils import cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, Blueprint
from flask.config import Config
from flask.helpers import locked_cached_property, get_root_path

from starlit.util.helpers import find_modules, import_modules
from starlit.util.fixtures import _Fixtured


# contenttype handler functions are stored like this
handler_opts = namedtuple('PageContentTypeHandler', 'view_func methods module')


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


class StarlitModule(Blueprint, _Fixtured):
    """StarlitModule is a :class:`flask.Blueprint` with some extras
    
    This class adds the ability to register custom page handlers and
    editable settings which can be safely edited by the user on runtime.

    Basically  you can initialize it like other flask blueprints
    """
    
    def __init__(self, name, import_name, *args, **kwargs):
        self.name = name
        self.import_name = import_name
        if kwargs.pop('builtin', False):
            self.name = "starlit-{}" .format(self.name)
        # flask wouldn't serve static files if this is not set 
        if not getattr(self, 'static_url_path', None):
            self.static_url_path="/static/" + self.name
        super(StarlitModule, self).__init__(
            self.name,
            self.import_name,
            static_url_path=self.static_url_path,
            *args, **kwargs)
        self.settings_providers = []
        self._content_type_handlers = {}

    def register(self, app, *args, **kwargs):
        super(StarlitModule, self).register(app, *args, **kwargs)
        # Update the app.config with our defaults
        app.config.from_module_defaults(self.root_path)
        # Add our page contenttype handlers to the app 
        for contenttype, opts in self._content_type_handlers.items():
            app._add_contenttype_handler(contenttype, **opts._asdict())

    def contenttype_handler(self, contenttype, methods):
        """Like :meth:`Starlit.contentype_handler` but for a module. """
        def wrapper(func):
            self._content_type_handlers[contenttype] = handler_opts(
                func,
                methods,
                module=self.name)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper

    def settings_provider(self, func):
        """Record a function as a setting provider

        Setting provider functions should return a list of options.
        This could be done easley using :class:`starlit.utils.option.Option`
        """
        self.settings_providers.append(func)
        def wrapped(*a, **kw):
            return func(*a, **kw)
        return wrapped

    def get_provided_settings(self):
        """Iterate over registered modules and return setting providers"""
        for provider in self.settings_providers:
            yield provider()


class Starlit(Flask):
    """Wrapps the :class:flask.Flask` to provide additional functionality.
    
    It add the following features:
        - Custom module system
        - Page contenttype handlers
        - Editable settings which are persisted to the database
        - Plugin support
    """
    
    # Custom configuration class :class:`StarlitConfig`
    config_class = StarlitConfig

    def __init__(self, *args, **kwargs):
        super(Starlit, self).__init__(*args, **kwargs)
        self.modules = {}
        self.plugins = {}
        self._page_contenttype_handlers = {}
        self._provided_settings = {}

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

    def _add_contenttype_handler(self, contenttype, view_func, methods=('GET',), module=None):
        self._page_contenttype_handlers[contenttype] = handler_opts(
            view_func,
            methods,
            module
            )

    def contenttype_handler(self, contenttype, methods):
        """A decorator to add custom contenttype handlers to be
        registered with the application

        .. Note::
            Functions decorated with this functions are treated like
            flask views.

        :param contenttype: a string that identify a certain page class
        :param methods: a list of HTTP methods that are accepted by this handler
        """
        def wrapper(func):
            self._add_contenttype_handler(func, contenttype, methods)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper

    def get_handler_for(self, contenttype):
        return self._page_contenttype_handlers.get(contenttype)

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
            starlit_modules = (v for v in module.__dict__.values() if isinstance(v, StarlitModule))
            for mod in set(starlit_modules):
                yield mod

    def _collect_provided_settings(self):
        for mod in self.modules.values():
            provider = getattr(mod, 'get_provided_settings', None)
            if provider is None:
                continue
            for provided in  provider():
                for p in provided:
                    p.module = mod
                    self._provided_settings[p.name] = p

    @property
    def provided_settings(self):
        """Iterate over registered modules to collect editable settings"""
        if not self._provided_settings:
            self._collect_provided_settings()
        return self._provided_settings.values()

    def use(self, plugin, *args, **kwargs):
        """Use the given plugin with this application"""
        plugin = plugin()
        plugin.init_app(self, *args, **kwargs)
        if plugin.needs_module_registration:
            self.register_module(plugin)
        self.plugins[plugin.name] = plugin
        return plugin
