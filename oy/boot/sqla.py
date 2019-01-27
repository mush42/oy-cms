from flask_sqlalchemy import SQLAlchemy, Model
from flask_migrate import Migrate
from sqlalchemy_continuum.plugins import FlaskPlugin
from sqlalchemy_continuum import make_versioned


class OyModelMixin:
    """Adds some helper methods to the base model."""

    @classmethod
    def get_or_create(cls, **kwargs):
        obj = cls.query.filter_by(**kwargs).one_or_none()
        if obj:
            return obj
        return cls(**kwargs)
        

db = SQLAlchemy(model_class=(OyModelMixin, Model,))
migrate = Migrate()
make_versioned(plugins=[FlaskPlugin()])
