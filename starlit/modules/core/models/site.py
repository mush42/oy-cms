from starlit.models.abstract import  Slugged
from starlit.modules.editable_settings.models import Settings
from starlit.boot.exts.sqla import db

class Site(Slugged, db.Model):
    __slugcolumn__ = 'name'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(
        db.Unicode(255),
        unique=True,
        nullable=False,
        info=dict(
            label='Site Name',
            description='Unique name to identify this site.'
        )
    )
    is_active = db.Column(
        db.Boolean,
        default=True,
        info=dict(
            label='Active By Default',
            description='The default site for urls'
        )
    )
    settings = db.relationship('Settings', backref="site", uselist=False)

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
        return "Site(name='{}')".format(self.name)
