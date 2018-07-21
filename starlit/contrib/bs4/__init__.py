# -*- coding: utf-8 -*-
"""
    starlit.contrib.bs4
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    Provides the minified css and js files of
    the latest version of bootstrap4 along
    with some helper jinja macros
"""
from starlit.wrappers import StarlitModule


bs4 = StarlitModule(
    'starlit.contrib.bs4',
    __name__,
    static_folder='static',
    template_folder='templates'
  )

