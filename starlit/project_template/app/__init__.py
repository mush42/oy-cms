#-*-coding: utf-8-*-
"""

    {{ appname }}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A starllit-cms project

    :copyright: your name 
"""
from starlit import create_app
from starlit_admin import StarlitAdmin


app = create_app(__name__, 'config.py')
admin = StarlitAdmin(app)
 