# -*- coding: utf-8 -*-
"""
    starlit
    ~~~~~~~~~~~~~~~~~~

    Initialize the application.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask import current_app
from flask_wtf import CSRFProtect
from starlit.boot.sqla import db, migrate
from starlit.boot.babel import babel, init_babel
from starlit.boot.security import initialize_security
from starlit.wrappers import Starlit
from starlit.exceptions import StarlitException
from starlit.boot.shell import make_shell_context
from starlit.boot.cli import register_cli_commands
from starlit.boot import boot_config
from starlit.core import core
from starlit.models import *


def initialize_builtin_extensions():
    """Initialize third-party extensions."""
    app = current_app._get_current_object()
    CSRFProtect(app)
    db.init_app(app)
    migrate.init_app(app, db=db)
    init_babel(app)
    initialize_security(app)


def _prepare_app(name, app_class, **kwargs):
    """Internal helper used by :func:`create_app` to initialize the application"""
    if not issubclass(app_class, Starlit):
        raise TypeError(
            """The application class should be a subclass of starlit.wrappers.Starlit."""
        )
    default_kwargs = dict(template_folder="templates", static_folder="static")
    [kwargs.setdefault(k, v) for k, v in default_kwargs.items()]
    return app_class(name, **kwargs)


def create_app(
    name,
    config=None,
    app_class=Starlit,
    envar="STARLIT_CONFIG",
    **kwargs):
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
            - The ``config`` parameter:
                - String: the same as config.from_pyfile
                - Dict: the same as config.from_mapping
                - Other: the same as config.from_object
            
        Note that modules registered later using :meth:`starlit.wrappers.Starlit: register_module`
        might override the default configurations set in this function
        You can configure the application through other means after initialization.

    :param name: Serves the same purpose as the name argument passed to :class:`flask.Flask`
    :param app_class: The application class to initialize
    :param config: Other configuration parameters 
    :param envar: The environment variable from which to load the configurations
    """
    app = _prepare_app(name, app_class, **kwargs)
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
        register_cli_commands()
    app.shell_context_processor(make_shell_context)
    app.register_module(core)
    return app
