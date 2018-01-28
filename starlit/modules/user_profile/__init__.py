from starlit.wrappers import StarlitModule


user_profile = StarlitModule('user', __name__)

from .models import *
