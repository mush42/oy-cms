# -*- coding: utf-8 -*-
"""
    starlit.contrib.security_template_module
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    If you want to override the default security templates,
    you should use this module
"""
from starlit.wrappers import StarlitModule
from starlit.contrib.bs4 import bs4


security_template_module = StarlitModule(
    "starlit.contrib.security_template_module",
    __name__,
    static_folder="static",
    template_folder="templates",
)


@security_template_module.record_once
def setup_security_tpl(state):
    if "starlit.contrib.bs4" not in state.app.modules:
        state.app.register_module(bs4)
