from sqlalchemy.ext.declarative import declared_attr
from flask import current_app
from flask_security import current_user
from starlit.boot.exts.sqla import db
from starlit.babel import lazy_gettext
from ._sqlaevent import SQLAEvent



class UserRelated(SQLAEvent):
    """User Related"""

    @declared_attr
    def user_id(cls):
        return db.Column(
            db.Integer,
            db.ForeignKey('user.id'),
            info=dict(label=lazy_gettext('Author'))
            )

    @declared_attr
    def author(cls):
        return db.relationship('User',
            info=dict(label=lazy_gettext('Author'), description=lazy_gettext(''))
            )

    def before_flush(self, session, is_modified):
        if self.user_id is None:
            if not current_app.testing:
                self.user_id = current_user.id
            else:
                self.user_id = 1
        if is_modified:
            if not current_app.testing:
                self.user_id = current_user.id
