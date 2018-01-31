from importlib import import_module
from warnings import warn
from werkzeug import import_string
from flask import Flask, Blueprint
from flask.config import Config
from starlit.util.helpers import find_modules, import_modules


class StarlitConfig(Config):
    def defaults_from_pkg_dir(self, package_name):
        for modname in find_modules(package_name):
            try:
                imported = import_module("%s.defaults" %(modname))
                self.from_object(imported)
            except ImportError:
                continue


class StarlitModule(Blueprint):

    def __init__(self, name, import_name, *args, **kwargs):
        self.name = name
        self.import_name = import_name
        if kwargs.pop('builtin', False):
            self.name = "starlit-{}" .format(self.name)
            if not import_name.startswith("starlit."):
                self.import_name = "starlit.modules.{}".format(import_name)
        super(StarlitModule, self).__init__(self.name, self.import_name, *args, **kwargs)
        self.settings_providers = []
        self.finalize_funcs = []

    def register(self, app, *args, **kwargs):
        super(StarlitModule, self).register(app, *args, **kwargs)
        import_name = self.import_name
        pymod = import_string(import_name)
        if not pymod.__file__.endswith("__init__.py"):
            # A module, try to get the parent package
            import_name = ".".join(import_name.rsplit(".")[:-1])
        defaults_mod = import_string(import_name + ".defaults", silent=True)
        app.config.from_object(defaults_mod)
        # Run the finalization functions
        for f in self.finalize_funcs:
            f(app)


    def settings_provider(self, func):
        self.settings_providers.append(func)
        def wrapped(*a, **kw):
            return func(*a, **kw)
        return wrapped

    def after_setup(self, func):
        self.finalize_funcs.append(func)
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
        self.modules = self.blueprints
        self.plugins = {}

    def register_module(self, module, **options):
        super(Starlit, self).register_blueprint(blueprint=module, **options)

    def find_starlit_modules(self, pkg):
        found_modules = set()
        for module in import_modules(pkg):
            modname = module.__name__
            if modname in self.config['EXCLUDED_MODULES']:
                continue
            starlit_modules = (v for k,v in module.__dict__.items() if isinstance(v, StarlitModule))
            if starlit_modules:
                found_modules.add(modname)
            for mod in starlit_modules:
                yield mod

    def provided_settings(self):
        opts = []
        for mod in self.modules.values():
            provider = getattr(mod, 'get_provided_settings', None)
            if provider is None:
                continue
            for provided in  provider():
                for p in provided:
                    p.module = mod
                opts.extend(provided)
        return opts

    def use(self, plugin, *args, **kwargs):
        plugin = plugin()
        self.plugins[plugin.identifier] = plugin
        plugin.init_app(self, *args, **kwargs)
        if plugin.needs_module_registration:
            self.register_module(plugin)
        return plugin
