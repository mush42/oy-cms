from oy.wrappers import OyModule
from oy.helpers import increment_string


class OyExtBase(OyModule):

    # A dictionary holding OyModule initialization params
    module_args = None

    def __init__(self, app=None):
        self.reg_as_module = self.module_args is not None
        if self.reg_as_module:
            super().__init__(**self.module_args)
        if app:
            self._inner_init_app(app)

    def _inner_init_app(self, app):
        if self.reg_as_module:
            while self.name in app.modules:
                self.name = increment_string(self.name)
            app.register_module(self)
        self.init_app(app)

    def init_app(self, app):
        """Do the work here"""
        pass
