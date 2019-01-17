import pytest

def concrete_model(db, cls_name, bases, d):
    bases = list(bases) + [db.Model]
    attrs = dict(
        id=db.Column(db.Integer, primary_key=True), __tablename__=cls_name.lower()
    )
    attrs.update(d or {})
    model = type(cls_name, tuple(bases), attrs)
    db.create_all()
    return model


@pytest.fixture()
def makemodel(db):
    def func(clsname, bases=(), d=None):
        return concrete_model(db, clsname, bases, d)

    return func
