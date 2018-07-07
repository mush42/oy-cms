from starlit.wrappers import StarlitModule


user_profile = StarlitModule('user', __name__, builtin=True)

from .models import *
