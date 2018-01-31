from starlit.boot.context_processors import register_context_processors
from starlit.boot.templating import register_template_filters
from starlit.boot.exts.extension_registry import initialize_core_exts
from starlit.boot.exts.jinja import  EditableExtension
from starlit import models
from starlit.wrappers import Starlit


def create_app(app_class=Starlit, config=None, *args, **kwargs):
    default_kwargs = dict(
        template_folder='resources/templates',
        static_folder='resources/static'
    )
    [kwargs.setdefault(k, v) for k,v in default_kwargs.items()]
    app = app_class('starlit', *args, **kwargs)
    app.config.defaults_from_pkg_dir(__name__)
    app.config.from_envvar('STARLIT_CONFIG', True)
    app.config.from_mapping(config or dict())
    initialize_core_exts(app)
    for module in app.find_starlit_modules('starlit.modules'):
        app.register_module(module)
    register_context_processors(app)
    register_template_filters(app)
    app.jinja_env.extensions['starlit.boot.exts.jinja.EditableExtension'] = EditableExtension(app.jinja_env)
    return app

