from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from flask_security import current_user as security_current_user
from werkzeug.local import LocalProxy
from starlit.boot.exts.sqla import db
from starlit.babel import lazy_gettext
from ._sqlaevent import SQLAEvent

def _test_aware_current_user():
    if current_app.config['DEBUG'] and current_app.testing:
        return current_app.test_user
    return security_current_user

current_user = LocalProxy(lambda: _test_aware_current_user())

class UserRelated(SQLAEvent):
    """User Related"""

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
            onupdate=lambda: current_user.id,
            nullable=True,
            info=dict(label=lazy_gettext('Author'))
            )

    @declared_attr
    def last_edited_by(cls):
        return db.relationship(
            'User',
            foreign_keys=[cls.editor_id],
            info=dict(label=lazy_gettext('Author'), description=lazy_gettext(''))
            )

