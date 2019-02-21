# -*- coding: utf-8 -*-
"""
    oy.contrib.users.model
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Provides the user profile model.

    :copyright: (c) 2018 by Musharraf Omer.
    :license: MIT, see LICENSE for more details.
"""

from sqlalchemy import event, inspect
from sqlalchemy.orm import backref, mapper
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from flask_security import UserMixin, RoleMixin
from oy.boot.sqla import db
from oy.babel import lazy_gettext
from oy.models.abstract import TimeStampped, ReadOnlyProxiedDictMixin, DynamicPropWithFile, SQLAEvent
from oy.models import User


class Profile(ReadOnlyProxiedDictMixin, db.Model, TimeStampped):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False,
        info=dict(label=lazy_gettext("User")),
    )
    user = db.relationship(
        User,
        backref=backref("profile", uselist=False),
        cascade="delete, delete-orphan",
        single_parent=True,
        info=dict(label=lazy_gettext("User"), description=lazy_gettext("")),
    )
    extras = db.relationship(
        "ProfileExtras", collection_class=attribute_mapped_collection("key")
    )
    _proxied = association_proxy("extras", "value")

    def __repr__(self):
        return f"<{self.user.user_name}: Profile()>"


class ProfileExtras(DynamicPropWithFile, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey("profile.id"))


@event.listens_for(mapper, "init")
def add_user_profile(target, *args, **kwargs):
    if isinstance(target, User) and not getattr(target, "profile", None):
        target.profile = Profile()
