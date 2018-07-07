# -*- coding: utf-8 -*-
"""	
    starlit.models.abstract.user_related
    ~~~~~~~~~~

    Provides user related mixin class

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from flask_security import current_user as security_current_user
from werkzeug.local import LocalProxy
from starlit.boot.sqla import db
from starlit.babel import lazy_gettext
from ._sqlaevent import SQLAEvent

def _test_aware_current_user():
    # TODO: a very ugly approach. Remove it ASAP
    if current_app.config['DEBUG'] and current_app.testing:
        return current_app.test_user
    return security_current_user

current_user = LocalProxy(lambda: _test_aware_current_user())

class UserRelated(SQLAEvent):
    """A Mixin class that provide the User Related fields"""

    @declared_attr
    def author_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('user.id'),
            default=lambda: current_user.id,
            nullable=False,
            info=dict(label=lazy_gettext('Author'))
            )

    @declared_attr
    def author(cls):
        return db.relationship(
            'User',
            foreign_keys=[cls.author_id],
            info=dict(label=lazy_gettext('Author'), description=lazy_gettext(''))
            )

    @declared_attr
    def editor_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('user.id'),
            nullable=True,
            #onupdate=lambda: current_user.id,
            info=dict(label=lazy_gettext('Author'))
            )

    @declared_attr
    def last_edited_by(cls):
        return db.relationship(
            'User',
            foreign_keys=[cls.editor_id],
            info=dict(label=lazy_gettext('Author'), description=lazy_gettext(''))
            )

