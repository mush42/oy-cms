from starlit.wrappers import StarlitModule

class StarlitPlugin(StarlitModule):
    """The base class for all starlit plugins"""

    def __init__(self):
        self.needs_blueprint_registration = getattr(self, 'needs_blueprint_registration', False) 
        self.blueprint_opts = getattr(self, 'blueprint_opts', None) or {}
        if not self.blueprint_opts:
            self.blueprint_opts['name'] = self.identifier
            self.blueprint_opts['import_name'] = self.__module__
        super(StarlitPlugin, self).__init__(
            name=self.blueprint_opts.pop('name'),
            import_name=self.blueprint_opts.pop('import_name'),
            builtin=False, **self.blueprint_opts
        )

    def init_app(self, app, *args, **kwargs):
        """Implement the plugin logic here"""
        raise NotImplementedError

    @property
    def identifier(self):
        """The name to access this plugin"""
        raise NotImplementedError