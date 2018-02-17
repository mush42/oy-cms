# -*- coding: utf-8 -*-
"""	
    starlit.plugin
    ~~~~~~~~~~

    Provides the plugin class which all starlit plugins should inherit from.

    .. Note: Light Weight Integration

        This is not a plugin system, instead, it provides an entry point
        to integrate other flask extensions or to add custom functionality

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from flask_sqlalchemy.model import camel_to_snake_case
from starlit.wrappers import StarlitModule


class StarlitPlugin(StarlitModule):
    """The base class for all starlit plugins.

        This is not a plugin system. Instead, it provides
        an entry point for lightweight integration with
        other flask extensions, and/or the addition of
        custom functionality.

    The plugin should not accept any arguments in its :meth:`__init__`
    instead, all necessary arguments will be passed to :meth:`init_app` 
    """
    
    # should we register this as a starlit module , so the plugin can
    # extend the app with custom routes and context processors ..etc
    needs_module_registration = False
    # Any keyword arguments to initialize the blueprint 
    # should be set to this class level variable as a dictionary
    blueprint_opts = None

    def __init__(self):
        if self.blueprint_opts is None:
            self.blueprint_opts = {}
        self.blueprint_opts.setdefault('import_name', self.__module__)
        if not self.__dict__.get('name', ''):
            name = camel_to_snake_case(self.__class__.__name__)
            self.blueprint_opts.setdefault('name', name)
        super(StarlitPlugin, self).__init__(
            name=self.blueprint_opts.pop('name'),
            import_name=self.blueprint_opts.pop('import_name'),
            builtin=False, **self.blueprint_opts
        )

    def init_app(self, app, *args, **kwargs):
        """Implement the plugin logic here
        
        This method will be called when using the plugin with
        a specific app instance.
        
        Any variables required to configure this plugin are passed as
        positional and keyword arguments to this method.
        """
        raise NotImplementedError

