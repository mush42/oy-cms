# -*- coding: utf-8 -*-
"""
    starlit.contrib.admin.resource_module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Create an admin module to be able to
    overide default `flask_admin` templates.
"""
from starlit.wrappers import StarlitModule

admin_resource_module = StarlitModule(
    name="starlit-admin",
    import_name="starlit.contrib.admin.resource_module",
    static_folder="static",
    template_folder="templates",
)
