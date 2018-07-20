#-*-coding: utf-8-*-
"""

    {{ project_name }}
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    A starllit-cms project
"""
from starlit import create_app
from starlit_admin import StarlitAdmin


app = create_app('{{project_name}}', 'config.py')
admin = StarlitAdmin(app)
 