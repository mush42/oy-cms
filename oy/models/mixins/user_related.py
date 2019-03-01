# -*- coding: utf-8 -*-
"""	
    oy.models.mixins.user_related
    ~~~~~~~~~~

    Provides user related mixin class

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy.ext.declarative import declared_attr
from flask import current_app, _request_ctx_stack
from flask_security import current_user
from oy.boot.sqla import db
from oy.babel import lazy_gettext
from ._sqlaevent import SQLAEvent


class UserRelated(SQLAEvent):
    """A Mixin class that provide the User Related fields"""

    @declared_attr
    def author_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey("user.id"),
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
            info=dict(label=lazy_gettext("Author")),
        )

    @declared_attr
    def last_edited_by(cls):
        return db.relationship(
            "User",
            foreign_keys=[cls.editor_id],
            info=dict(label=lazy_gettext("Author"), description=lazy_gettext("")),
        )

    def before_flush(self, session, is_modified):
        if _request_ctx_stack.top is not None:
            if not is_modified:
                self.author_id = current_user.id
            else:
                self.editor_id = current_user.id
