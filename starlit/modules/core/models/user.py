from sqlalchemy import inspect
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from flask_security import UserMixin, RoleMixin
from flask_security.utils import hash_password
from starlit.boot.exts.sqla import db
from starlit.babel import lazy_gettext
from starlit.models.abstract import TimeStampped, ProxiedDictMixin, DynamicProp, SQLAEvent


roles_users = db.Table('roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True,
        info=dict(label=lazy_gettext('Name'), description=lazy_gettext('A name to identify this role'))
    )
    description = db.Column(db.Unicode(255),
        info=dict(label=lazy_gettext('Description'), description=lazy_gettext('A simple summary about this role.'))
    )

    def __str__(self):
        return self.name


class User(db.Model, UserMixin, SQLAEvent):
    __slugcolumn__ = 'user_name'
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.Unicode(128), nullable=False, unique=True, index=True,
        info=dict(label=lazy_gettext('User Name'), description=lazy_gettext('A unique name for this user (used for login)'))
    )
    email = db.Column(db.String(255), unique=True,
        info=dict(label=lazy_gettext('Email'), description=lazy_gettext(''))
    )
    password = db.Column(db.String(255),
        info=dict(label=lazy_gettext('Password'), description=lazy_gettext(''))
    )
    active = db.Column(db.Boolean,
        info=dict(label=lazy_gettext('Active'), description=lazy_gettext('Activate or deactivate this user account'))
    )
    confirmed_at = db.Column(db.DateTime(),
        info=dict(label=lazy_gettext('Confirmed At'))
    )
    roles = db.relationship('Role', secondary=roles_users,
        backref=db.backref('users', lazy='dynamic'),
        info=dict(label=lazy_gettext('Roles'), description=lazy_gettext(''))
    )    
    name = property(fget=lambda self: self.profile.name)

    def __str__(self):
        return self.user_name

    def __repr__(self):
        return 'User(user_name={})'.format(self.user_name)

    def before_commit(self, session, is_modified):
        needs_hash = any((
          not is_modified,
          is_modified and 'password' not in inspect(self).unmodified
        ))
        if needs_hash:
            self.password = hash_password(self.password)
