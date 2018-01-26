from starlit.models.abstract import  SQLAEvent
from starlit.boot.exts.sqla import db
from .settings import Settings


class SettingsProfile(SQLAEvent, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Unicode(255),
        unique=True,
        nullable=False,
        info=dict(
            label='Profile Name:',
            description='A Unique name for this settings profile.'
        )
    )
    is_active = db.Column(
        db.Boolean,
        default=False,
        info=dict(
            label='Active',
            description='Sets or unsets this settings profile as the default profile'
        )
    )
    settings = db.relationship('Settings', backref="profile", uselist=False)

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
