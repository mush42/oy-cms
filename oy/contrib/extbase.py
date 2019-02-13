from oy.wrappers import OyModule


class OyExtBase(OyModule):

    # A unique name that identifies this ext 
    # Can be omitted if  providing a name key in the module_args dict
    name = None
    # A dictionary holding OyModule initialization params
    module_args = None

    def __init__(self, app=None, **module_args):
        self.reg_as_module = self.module_args is not None
        if self.reg_as_module:
            for key, value in module_args.items():
                self.module_args.setdefault(key, value)
            super().__init__(**self.module_args)
        if not self.name:
            raise AttributeError("A name is required to identify this extension")
        if app:
            self._inner_init_app(app)

    def _inner_init_app(self, app):
        _oy_contrib_exts = app.data.setdefault("_oy_contrib_extensions", [])
        if self.name not in _oy_contrib_exts:
            _oy_contrib_exts.append(self.name)
        else:
            raise RuntimeError(f"The extension {self.name} is already registered with the application {app}.")
        if self.reg_as_module:
            app.register_module(self)
        self.init_app(app)

    def init_app(self, app):
        """Do the work here"""
        pass
