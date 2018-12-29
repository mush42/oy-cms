from itertools import chain
from sqlalchemy.orm import relationship
from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import association_proxy
from flask import current_app
from oy.boot.sqla import db
from oy.models.abstract import SQLAEvent, ProxiedDictMixin, DynamicProp
from oy.dynamicform import Field


class SettingsProfile(SQLAEvent, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Unicode(255),
        unique=True,
        nullable=False,
        info=dict(
            label="Profile Name:",
            description="A Unique name for this settings profile.",
        ),
    )
    is_active = db.Column(
        db.Boolean,
        default=False,
        info=dict(
            label="Active",
            description="Sets or unsets this settings profile as the default profile",
        ),
    )
    settings = db.relationship("Settings", backref="profile", uselist=False)

    def on_init(self):
        if self.settings is None:
            self.settings = Settings()

    def before_flush(self, session, is_modified):
        active = session.query(self.__class__).filter_by(is_active=True).all()
        if active:
            for instance in active:
                instance.is_active = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return "SettingsProfile(name='{}')".format(self.name)


class SettingCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)

    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_or_create(name):
        try:
            return SettingCategory.query.filter(SettingCategory.name == name).one()
        except NoResultFound:
            cat = SettingCategory(name)
            db.session.add(cat)
            return cat


class Setting(DynamicProp, db.Model):
    __tablename__ = "setting"
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("settings.id"))
    category_id = db.Column(db.Integer, db.ForeignKey("setting_category.id"))
    cat = relationship("SettingCategory", backref="settings")

    category = association_proxy("cat", "name", creator=SettingCategory.get_or_create)

    def __repr__(self):
        return "<Setting key={}><category:{}>".format(self.key, self.category)


class Settings(ProxiedDictMixin, db.Model, SQLAEvent):
    id = db.Column(db.Integer, primary_key=True)
    store = db.relationship(
        "Setting", collection_class=attribute_mapped_collection("key")
    )
    _proxied = association_proxy("store", "value")
    profile_id = db.Column(
        db.Integer, db.ForeignKey("settings_profile.id"), nullable=False
    )

    def on_init(self):
        process_func = lambda seq: [Field(**d) for d in seq]
        ready = ((c, process_func(l)) for c, l in current_app.provided_settings)
        for category, opts in ready:
            for opt in opts:
                setting = Setting(key=opt.name)
                setting.value = opt.default
                setting.category = str(category)
                self.store[opt.name] = setting
