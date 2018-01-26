from importlib import import_module
from warnings import warn
from flask import Flask, Blueprint
from flask.config import Config
from starlit.util.helpers import find_modules, import_modules


class StarlitConfig(Config):
    def from_package_defaults(self, package_name):
        for modname in find_modules(package_name):
            try:
                imported = import_module("%s.defaults" %(modname))
                self.from_object(imported)
            except ImportError:
                continue


class StarlitModule(Blueprint):

    def __init__(self, *args, **kwargs):
        args = list(args)
        super(StarlitModule, self).__init__("starlit-%s" %args.pop(0), *args, **kwargs)
        self.settings_providers = []
        self.finalize_funcs = []

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
        self.blueprint_packages = []

    def find_blueprints(self, basemodule):
        for module in import_modules(basemodule):
            modname = module.__name__
            if modname in self.config['EXCLUDED_MODULES']:
                continue
            starlit_modules = (v for k,v in module.__dict__.items() if isinstance(v, StarlitModule))
            if starlit_modules and modname not in self.blueprint_packages:
                self.blueprint_packages.append(modname)
            for bp in starlit_modules:
                yield bp

    def setup_features(self):
        enabled = self.config['ENABLED_FEATURES']
        disable_opts = self.config['FEATURE_DISABLE']
        for package_name in self.blueprint_packages:
            for feature in enabled:
                if package_name in disable_opts and feature_name in disable_opts['package_name']:
                    continue
                try:
                    import_module("%s.%s" %(package_name, feature))
                except ImportError:
                    if not self.testing:
                        warn(f"Skipping optional module: {package_name}.{feature}. Module does not exist.")
                    continue
    
    def provided_settings(self):
        opts = []
        for bp in self.blueprints.values():
            provider = getattr(bp, 'get_provided_settings', None)
            if provider is None:
                continue
            for provided in  provider():
                for p in provided:
                    p.blueprint = bp
                opts.extend(provided)
        return opts

