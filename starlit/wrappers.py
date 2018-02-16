import sys
import os
from collections import namedtuple
from importlib import import_module
from warnings import warn
from werkzeug import import_string
from werkzeug.utils import cached_property
from jinja2 import ChoiceLoader, FileSystemLoader
from flask import Flask, Blueprint
from flask.config import Config
from flask.helpers import locked_cached_property, get_root_path
from starlit.util.helpers import find_modules, import_modules
from starlit.util.fixtures import _Fixtured


handler_opts = namedtuple('PageContentTypeHandler', 'view_func methods module')

class StarlitConfig(Config):
    def from_module_defaults(self, import_name):
        pymod = sys.modules[import_name]
        if not pymod.__file__.endswith("__init__.py"):
            # A module, try to get the parent package
            import_name = ".".join(import_name.rsplit(".")[:-1])
        defaults_mod = import_string(import_name + ".defaults", silent=True)
        self.from_object(defaults_mod)


class StarlitModule(Blueprint, _Fixtured):

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
        app.config.from_module_defaults(self.import_name)
        for contenttype, opts in self._content_type_handlers.items():
            app._add_contenttype_handler(contenttype, **opts._asdict())

    def contenttype_handler(self, contenttype, methods):
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
        self.settings_providers.append(func)
        def wrapped(*a, **kw):
            return func(*a, **kw)
        return wrapped

    def get_provided_settings(self):
        for provider in self.settings_providers:
            yield provider()


class Starlit(Flask):
    config_class = StarlitConfig

    def __init__(self, *args, **kwargs):
        super(Starlit, self).__init__(*args, **kwargs)
        self.modules = {}
        self.plugins = {}
        self._page_contenttype_handlers = {}
        self._provided_settings = {}

    @locked_cached_property
    def jinja_loader(self):
        """Starlit modules should have higher priority"""
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
        def wrapper(func):
            self._add_contenttype_handler(func, contenttype, methods)
            def wrapped(*a, **kw):
                return func(*a, **kw)
            return wrapped
        return wrapper

    def get_handler_for(self, contenttype):
        return self._page_contenttype_handlers.get(contenttype)

    def register_module(self, module, **options):
        super(Starlit, self).register_blueprint(blueprint=module, **options)
        self.modules[module.name] = module

    def find_starlit_modules(self, pkg):
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
        if not self._provided_settings:
            self._collect_provided_settings()
        return self._provided_settings.values()

    def use(self, plugin, *args, **kwargs):
        plugin = plugin()
        self.plugins[plugin.name] = plugin
        plugin.init_app(self, *args, **kwargs)
        if plugin.needs_module_registration:
            self.register_module(plugin)
        return plugin
