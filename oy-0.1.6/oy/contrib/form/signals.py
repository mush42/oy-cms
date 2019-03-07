# -*- coding: utf-8 -*-
"""
    oy.contrib.form.signals
    ~~~~~~~~~~~~~~~~~~~~~

    Some helpfull signals related to form submissions.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""
from blinker import Namespace

_signals = Namespace()


before_accepting_submission = _signals.signal("before-accepting-submission")
new_submission_received = _signals.signal("new-submission-received")
