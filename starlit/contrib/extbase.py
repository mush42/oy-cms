from starlit.wrappers import StarlitModule


class StarlitExtBase(StarlitModule):

    # A dictionary holding StarlitModule initialization params
    module_args = None

    def __init__(self, app=None):
        if self.module_args is not None:
            super().__init__(**self.module_args)
        if app:
            self._inner_init_app(app)

    def _inner_init_app(self, app):
        if self.module_args is not None:
            app.register_module(self)
        self.init_app(app)

    def init_app(self, app):
        """Do the work here"""
        pass
