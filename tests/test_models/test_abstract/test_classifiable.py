import pytest
from oy.models.abstract import Tagged, Categorized


def test_tagged_basic(db, makemodel):
    Philosopher = makemodel(
        "Philosopher", (Tagged,), dict(name=db.Column(db.String(50)))
    )
    socrates = Philosopher(name="Socrates")
    archimedes = Philosopher(name="Archimedes")
    plato = Philosopher(name="Plato", tags=["Great", "deep_thinker"])
    db.session.add_all([socrates, archimedes, plato])
    db.session.commit()
    assert not socrates.tags
    assert "Great" in plato.tags
    socrates.tags.extend(["Greek", "philosophy"])
    archimedes.tags.extend(["Greek", "math"])
    db.session.commit()
    greek = Philosopher.Tag.query.filter_by(title="Greek").one()
    assert all(g in greek.objects for g in [socrates, archimedes])


def test_tagged_with_inheritance(db):
    class Person(db.Model, Tagged):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        type = db.Column(db.String(50))
        __mapper_args__ = {"polymorphic_identity": "person", "polymorphic_on": "type"}

    class Employee(Person):
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "employee"}

    class Manager(Person):
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "manager"}

    assert Person.Tag is Employee.Tag
    assert Person.Tag is Manager.Tag


def test_categorized(db, makemodel):
    Language = makemodel("Language", (Categorized,), {"code": db.Column(db.String(50))})
    arabic = Language(code="ar")
    english = Language(code="en")
    frensh = Language(code="fr")
    persian = Language(code="fa")
    rtllang = Language.Category(title="Right to left")
    ltrlang = Language.Category(title="Left to right")
    canadalang = Language.Category(title="Spoken in Canada")
    arabic.category = rtllang
    persian.category = rtllang
    english.category = ltrlang
    frensh.category = canadalang
    db.session.add_all([english, frensh, arabic, persian])
    db.session.commit()
    assert english.category == ltrlang
    assert (
        persian
        in Language.Category.query.filter_by(title="Right to left").one().objects
    )
