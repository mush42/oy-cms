from sqlalchemy.orm.collections import attribute_mapped_collection
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.ext.associationproxy import association_proxy
from flask import current_app, _app_ctx_stack
from starlit.boot.exts.sqla import db
from starlit.models.abstract import SQLAEvent, ProxiedDictMixin, DynamicProp



class SettingCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    settings = db.relationship('Setting', backref='category')


class Setting(DynamicProp, db.Model):
    __tablename__ = 'setting'
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('settings.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('setting_category.id'))

    def __repr__(self):
        return '<Setting key={}><category:{}>'.format(self.key, self.category)

class Settings(ProxiedDictMixin, db.Model, SQLAEvent):
    id =  db.Column(db.Integer, primary_key=True)
    options = db.relationship("Setting", collection_class=attribute_mapped_collection('key'))
    _proxied = association_proxy("options", "value")
    profile_id = db.Column(db.Integer, db.ForeignKey('settings_profile.id'), nullable=False)

    def on_init(self):
        ctx = _app_ctx_stack.top
        if not getattr(ctx, 'app_categories', None):
            ctx.app_categories = {}
            for opt in current_app.provided_settings:
                ctx.app_categories[opt.category] = SettingCategory(name=opt.category)
        for option in current_app.provided_settings:
            setting = Setting(key=option.name)
            setting.value = option.default
            setting.category = ctx.app_categories[option.category]
            self.options[option.name] = setting
