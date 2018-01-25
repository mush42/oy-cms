from sqlalchemy import event, inspect
from sqlalchemy.orm import mapper
from sqlalchemy.orm import backref
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.ext.associationproxy import association_proxy
from flask_security import UserMixin, RoleMixin
from starlit.boot.exts.sqla import db
from starlit.babel import lazy_gettext
from starlit.models.abstract import TimeStampped, ProxiedDictMixin, DynamicProp, SQLAEvent
from starlit.modules.core.models import User
from . import user_profile

class Profile(ProxiedDictMixin, db.Model, TimeStampped):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=True, nullable=False,
        info=dict(label=lazy_gettext('User'))
    )
    user = db.relationship(User, backref=backref("profile", uselist=False), cascade="delete, delete-orphan", single_parent=True,
        info=dict(label=lazy_gettext('User'), description=lazy_gettext(''))
    )
    extras = db.relationship("ProfileExtras", collection_class=attribute_mapped_collection('key'))
    _proxied = association_proxy("extras", "value")
    first_name = db.Column(db.Unicode(255), default="",
        info=dict(label=lazy_gettext('First Name'), description=lazy_gettext(''))
    )
    last_name = db.Column(db.Unicode(255), default="",
        info=dict(label=lazy_gettext('Last Name'), description=lazy_gettext(''))
    )
    bio = db.Column(db.Text,
        info=dict(label=lazy_gettext('Biography'), description=lazy_gettext(''))
    )

    @property
    def name(self):
        return ' '.join([self.first_name, self.last_name])

    @name.setter
    def name(self, value):
        self.first_name, self.last_name = value

    def __str__(self):
        return "{}'s Profile".format(self.name)


class ProfileExtras(DynamicProp, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile.id'))




def add_user_profile(target, *args, **kwargs):
    if isinstance(target, User) and not getattr(target, "profile", None):
        target.profile = Profile()


@user_profile.after_setup
def register_user_profiles_event_listener(app):
    event.listen(mapper, 'init', add_user_profile)