# -*- coding: utf-8 -*-
"""
    oy._prepare_app
    ~~~~~~~~~~~~~~~~~~

    Initialize the application.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask import current_app
from flask_wtf import CSRFProtect
from oy.boot.sqla import db, migrate
from oy.boot.babel import babel
from oy.boot.security import initialize_security
from oy.boot.shell import make_shell_context
from oy.boot import boot_config
from oy.wrappers import Oy
from oy.exceptions import OyException
from oy.core import core
from oy.models import *


def initialize_builtin_extensions():
    """Initialize third-party extensions."""
    app = current_app._get_current_object()
    CSRFProtect(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    babel.init_app(app)
    initialize_security(app)


def _prepare_app_internal(name, app_class, **kwargs):
    """Internal helper used by :func:`create_app` to initialize the application"""
    if not issubclass(app_class, Oy):
        raise TypeError(
            """The application class should be a subclass of oy.wrappers.Oy."""
        )
    default_kwargs = dict(template_folder="templates", static_folder="static")
    [kwargs.setdefault(k, v) for k, v in default_kwargs.items()]
    return app_class(name, **kwargs)


def prepare_app(name, config=None, app_class=Oy, envar="STARLIT_CONFIG", **kwargs):
    """This app factory is the main entry point of Oy.

    Use this function to create a new instance of
    :class:`flask.Flask` with all oy features configured for you, example::
    
        from oy import create_app
        
        config = dict(
          DEBUG=True,
        )
        app = create_app(__name__, config=config)

    .. Note:: The app_class argument

        Usually you don't need to pass this argument unless you have a
        special usage that requires customization of the app class.
        In this case you should sub-class :class:oy.wrappers.Oy`
        and pass the custom class to this function.

    .. Note:: Application Configuration

        By default, this function configures the app using:
            - Default configurations of modules registered with the application
            - An environment variable called **STARLIT_CONFIG** if exists
            - The ``config`` parameter:
                - String: the same as config.from_pyfile
                - Dict: the same as config.from_mapping
                - Other: the same as config.from_object
            
        Note that modules registered later using :meth:`oy.wrappers.Oy: register_module`
        might override the default configurations set in this function
        You can configure the application through other means after initialization.

    :param name: Serves the same purpose as the name argument passed to :class:`flask.Flask`
    :param app_class: The application class to initialize
    :param config: Other configuration parameters 
    :param envar: The environment variable from which to load the configurations
    """
    app = _prepare_app_internal(name, app_class, **kwargs)
    app.config.from_object(boot_config)
    app.config.from_envvar(envar, True)
    if isinstance(config, dict):
        app.config.from_mapping(config)
    elif isinstance(config, str):
        app.config.from_pyfile(config)
    else:
        app.config.from_object(config)
    with app.app_context():
        initialize_builtin_extensions()
    app.shell_context_processor(make_shell_context)
    app.register_module(core)
    return app
