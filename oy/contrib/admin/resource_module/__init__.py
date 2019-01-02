# -*- coding: utf-8 -*-
"""
    oy.contrib.admin.resource_module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Create an admin module to be able to
    overide default `flask_admin` templates.
"""
from oy.wrappers import OyModule

admin_resource_module = OyModule(
    name="oy.contrib.admin.resource_module",
    import_name="oy.contrib.admin.resource_module",
    static_folder="static",
    template_folder="templates",
)
