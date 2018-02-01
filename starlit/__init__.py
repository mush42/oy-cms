from starlit.exceptions import StarlitException
from starlit.boot import defaults as boot_config
from starlit.boot.context_processors import register_context_processors
from starlit.boot.templating import register_template_filters
from starlit.boot.exts.extension_registry import initialize_core_exts
from starlit.boot.exts.jinja import  EditableExtension
from starlit import models
from starlit.wrappers import Starlit


def _prepare_app(name, app_class, *args, **kwargs):
    if not issubclass(app_class, Starlit):
        raise TypeError("""The application class should be a subclass of starlit.wrappers.Starlit.""")
    default_kwargs = dict(
        template_folder='templates',
        static_folder='static'
    )
    [kwargs.setdefault(k, v) for k,v in default_kwargs.items()]
    return app_class(name, **kwargs)


def create_app(name, app_class=Starlit, config=None, *args, **kwargs):
    app = _prepare_app(name, app_class, *args, **kwargs)
    app.config.from_object(boot_config)
    app.config.from_envvar('STARLIT_CONFIG', True)
    app.config.from_mapping(config or dict())
    initialize_core_exts(app)
    for module in app.find_starlit_modules('starlit.modules'):
        app.register_module(module)
    register_context_processors(app)
    register_template_filters(app)
    app.jinja_env.extensions['starlit.boot.exts.jinja.EditableExtension'] = EditableExtension(app.jinja_env)
    return app

