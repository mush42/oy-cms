# -*- coding: utf-8 -*-
"""
    starlit.core.security_resource_module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    If overriding security templates, this module will be registered
"""
from starlit.wrappers import StarlitModule


security_resource_module = StarlitModule('starlit.core.security_resource_module',
    __name__,
    static_folder='static',
    template_folder='templates'
  )

