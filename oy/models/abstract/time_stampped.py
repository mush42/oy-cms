# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.time_stampped
    ~~~~~~~~~~

    Provides a mixin classe for models that need to track time 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from oy.boot.sqla import db
from ._sqlaevent import SQLAEvent


class TimeStampped(SQLAEvent):
    """Add created and updated fields"""

    created = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        info=dict(label="Creation Date"),
    )
    updated = db.Column(
        db.DateTime,
        onupdate=datetime.utcnow,
        nullable=True,
        info=dict(label="Last Updated"),
    )
