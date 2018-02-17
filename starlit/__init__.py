# -*- coding: utf-8 -*-
"""
    starlit
    ~~~~~~~~~~~

    Starlit is a Micro Content Management System (CMS) for the modern web.
    It is based on Flask, and provides a full-fledged and flexible CMS
    engine with many customization hooks.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from starlit.exceptions import StarlitException
from starlit.boot import defaults as boot_config
from starlit.boot.context_processors import register_context_processors
from starlit.boot.templating import register_template_filters
from starlit.boot.exts.extension_registry import initialize_core_exts
from starlit.boot.exts.jinja import  EditableExtension
from starlit import models
from starlit.wrappers import Starlit


def _prepare_app(name, app_class, *args, **kwargs):
    """Internal helper used by :func:`create_app` to initialize the application"""
    if not issubclass(app_class, Starlit):
        raise TypeError("""The application class should be a subclass of starlit.wrappers.Starlit.""")
    default_kwargs = dict(
        template_folder='templates',
        static_folder='static'
    )
    [kwargs.setdefault(k, v) for k,v in default_kwargs.items()]
    return app_class(name, **kwargs)


def create_app(name, app_class=Starlit, config=None, *args, **kwargs):
    """This app factory is the main entry point of Starlit.

    Use this function to create a new instance of
    :class:`flask.Flask` with all starlit features configured for you, example::
    
        from starlit import create_app
        
        config = dict(
          DEBUG=True,
        )
        app = create_app(__name__, config=config)

    .. Note:: The app_class argument

        Usually you don't need to pass this argument unless you have a
        special usage that requires customization of the app class.
        In this case you should sub-class :class:starlit.wrappers.Starlit`
        and pass the custom class to this function.

    .. Note:: Application Configuration

        By default, this function configures the app using:
            - Default configurations of modules registered with the application
            - An environment variable called **STARLIT_CONFIG** if exists
            - The configuration dictionary passed as **config** argument
            
        Note that modules registered later using :meth:`starlit.wrappers.Starlit: register_module`
        might override the default configurations set in this function
        You can configure the application through other means after initialization.

    :param name: Serves the same purpose as the name argument passed to :class:`flask.Flask`
    :param app_class: The application class to initialize
    :param config: A dict of configuration values 
    """
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

