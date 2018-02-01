from flask_sqlalchemy.model import camel_to_snake_case
from starlit.wrappers import StarlitModule


class StarlitPlugin(StarlitModule):
    """The base class for all starlit plugins.
        This is not a plugin system. Instead, it provides
        an entry point for lightweight integration with
        other flask extensions, and/or the addition of
        custom functionality.
    """
    needs_module_registration = False

    def __init__(self):
        self.blueprint_opts = getattr(self, 'blueprint_opts', {})
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
        """Implement the plugin logic here"""
        raise NotImplementedError

