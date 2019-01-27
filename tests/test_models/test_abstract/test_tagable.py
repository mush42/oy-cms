import pytest
from oy.models.abstract import Tagable


def test_tagable_basic(db, makemodel):
    Philosopher = makemodel(
        "Philosopher",
        (Tagable,),
        dict(name=db.Column(db.String(50)))
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


def test_tagable_with_inheritance(db):
    class Person(db.Model, Tagable):
        id = db.Column(db.Integer, primary_key=True)
        name = db.Column(db.String(50))
        type = db.Column(db.String(50))
        __mapper_args = {"polymorphic_identity": "person", "polymorphic_on": "type"}

    class Employee(Person):
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        __mapper_args = {"polymorphic_identity": "employee"}

    class Manager(Person):
        id = db.Column(db.Integer, db.ForeignKey(Person.id), primary_key=True)
        __mapper_args = {"polymorphic_identity": "manager"}

    assert Person.Tag is Employee.Tag 
    assert Person.Tag is Manager.Tag 
