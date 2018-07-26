from starlit.wrappers import StarlitModule
from .admin import register_admin


module = StarlitModule('app.module', __name__)
