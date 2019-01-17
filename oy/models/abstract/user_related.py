# -*- coding: utf-8 -*-
"""	
    oy.models.abstract.user_related
    ~~~~~~~~~~

    Provides user related mixin class

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from flask import current_app, _request_ctx_stack
from flask_security import current_user
from werkzeug.local import LocalProxy
from oy.boot.sqla import db
from oy.babel import lazy_gettext
from ._sqlaevent import SQLAEvent


def get_current_user_id():
    """Returns the current user id or the
    id for the firstly created user if no
    request context is present.
    """
    if _request_ctx_stack.top is None:
        user = db.metadata.tables["user"]
        return db.session.query(user).filter(user.c.active == True).first().id
    return current_user.id


class UserRelated(SQLAEvent):
    """A Mixin class that provide the User Related fields"""

    @declared_attr
    def author_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey("user.id"),
            default=get_current_user_id,
            nullable=False,
            info=dict(label=lazy_gettext("Author")),
        )

    @declared_attr
    def author(cls):
        return db.relationship(
            "User",
            foreign_keys=[cls.author_id],
            info=dict(label=lazy_gettext("Author"), description=lazy_gettext("")),
        )

    @declared_attr
    def editor_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey("user.id"),
            nullable=True,
            onupdate=get_current_user_id,
            info=dict(label=lazy_gettext("Author")),
        )

    @declared_attr
    def last_edited_by(cls):
        return db.relationship(
            "User",
            foreign_keys=[cls.editor_id],
            info=dict(label=lazy_gettext("Author"), description=lazy_gettext("")),
        )
