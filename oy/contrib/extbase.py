from oy.wrappers import OyModule


class OyExtBase(OyModule):

    # A dictionary holding OyModule initialization params
    module_args = None

    def __init__(self, app=None, **module_args):
        self.reg_as_module = self.module_args is not None
        if self.reg_as_module:
            for key, value in module_args.items():
                self.module_args.setdefault(key, value)
            super().__init__(**self.module_args)
        if app:
            self._inner_init_app(app)

    def _inner_init_app(self, app):
        if self.name in app.modules:
            raise RuntimeError(f"The extension {self.name} is already registered with the application {app}.")
        if self.reg_as_module:
            app.register_module(self)
        self.init_app(app)

    def init_app(self, app):
        """Do the work here"""
        pass
