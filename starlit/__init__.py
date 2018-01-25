from starlit.boot.context_processors import register_context_processors
from starlit.boot.templating import register_template_filters
from starlit.boot.exts import initialize_core_exts
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
    app.config.from_package_defaults('starlit')
    app.config.from_envvar('STARLIT_CONFIG', True)
    app.config.from_mapping(config or dict())
    initialize_core_exts(app)
    app.modules = []
    for blueprint in app.find_blueprints('starlit.modules'):
        app.register_blueprint(blueprint)
        app.modules.append(blueprint)
    app.setup_features()
    for m in app.modules:
        for f in m.finalize_funcs:
            f(app)
    register_context_processors(app)
    register_template_filters(app)
    app.jinja_env.extensions['starlit.boot.exts.jinja.EditableExtension'] = EditableExtension(app.jinja_env)
    return app

