# -*- coding: utf-8 -*-
"""
    starlit.contrib.security_template_module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    If you want to override the default security templates,
    you should use this module
"""
from starlit.wrappers import StarlitModule


security_template_module = StarlitModule(
    'starlit.contrib.security_template_module',
    __name__,
    static_folder='static',
    template_folder='templates'
  )

