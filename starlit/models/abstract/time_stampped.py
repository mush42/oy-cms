from datetime import datetime
from starlit.boot.exts.sqla import db
from ._sqlaevent import SQLAEvent

class TimeStampped(SQLAEvent):
    created = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        info=dict(
            label='Creation Date'
        )
    )
    updated = db.Column(
        db.DateTime,
        onupdate=datetime.utcnow,
        nullable=True,
        info=dict(
            label='Last Updated'
        )
    )
