from starlit import create_app
from starlit.contrib.admin import StarlitAdmin
from starlit.contrib.security_template_module import security_template_module
from .module import module


app = create_app(__name__, 'config.py')
admin = StarlitAdmin(app)
app.register_module(security_template_module)
app.register_module(module)
