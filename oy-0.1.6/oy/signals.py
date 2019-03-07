# -*- coding: utf-8 -*-
"""
    oy.signals
    ~~~~~~~~~~~~~~~~~~~~~

    Implements the core signals of oy.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from blinker import Namespace

# The namespace of oy signals
_signals = Namespace()


# All the following signals receives `app` as the sender

oy_module_registered = _signals.signal("oy-module-registered")

# When the app receives the first request
oy_app_starting = _signals.signal("oy-app-starting")
