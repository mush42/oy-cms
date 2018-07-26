# -*- coding: utf-8 -*-
"""
    starlit.signals
    ~~~~~~~~~~~~~~~~~~~~~

    Implements the core signals of starlit.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from blinker import Namespace

# The namespace of starlit signals
_signals = Namespace()


# All the following signals receives `app` as the sender
starlit_module_registered = _signals.signal('starlit-module-registered')
