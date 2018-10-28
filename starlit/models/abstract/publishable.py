# -*- coding: utf-8 -*-
"""	
    starlit.models.abstract.publishable
    ~~~~~~~~~~

    Provides a mixin classe for publishing content 

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property
from starlit.boot.sqla import db
from .time_stampped import TimeStampped


class Publishable(TimeStampped):
    """Add fields to track the publish status of the content """

    STATUS_CHOICES = [
        ("published", "Published"),
        ("draft", "Draft"),
        ("expired", "Expired"),
    ]
    status = db.Column(
        db.Enum(*[value for value, label in STATUS_CHOICES], name="status"),
        default=STATUS_CHOICES[0][0],
        info=dict(
            choices=STATUS_CHOICES,
            label="Status",
            description="The status of this content. Draft content will not be shown.",
        ),
    )
    publish_date = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False,
        info=dict(
            label="Publish Date",
            description="The content will not be publish until this date.",
        ),
    )
    expire_date = db.Column(
        db.DateTime,
        info=dict(
            label="Expiration Date",
            description="The content will not be publish After this date.",
        ),
    )

    @hybrid_property
    def is_published(self):
        rv = (
            self.status == self.STATUS_CHOICES[0][0]
            and self.publish_date <= datetime.now()
        )
        if self.expire_date is not None:
            rv = rv and self.expire_date >= datetime.now()
        return rv
