import pytest
from oy.models.abstract.misc import SelfRelated, Ordered


def test_self_related(db, makemodel):
    class SelfRel(SelfRelated, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        type = db.Column(db.String(50))

        __mapper_args__ = {"polymorphic_identity": "base_type", "polymorphic_on": type}

    class SubSelfRel(SelfRel):
        id = db.Column(db.Integer, db.ForeignKey(SelfRel.id), primary_key=True)
        __mapper_args__ = {"polymorphic_identity": "subselfrel"}

    db.create_all()

    instance = SelfRel()
    child = SubSelfRel()
    instance.children.append(child)
    db.session.add(instance)
    db.session.commit()
    parent = SubSelfRel()
    instance.parent = parent
    db.session.commit()
    assert instance.parent
    assert instance.children
    instance.children.remove(child)
    db.session.commit()
    assert not instance.children.count()
    db.session.delete(parent)
    db.session.commit()
    assert not SelfRel.query.all()


def test_ordered(db, makemodel):
    Ord = makemodel("Ord", (SelfRelated, Ordered))
    item1 = Ord()
    item2 = Ord()
    db.session.add(item1)
    db.session.commit()
    db.session.add(item2)
    db.session.commit()
    assert item1.sort_order == item1.id
    assert item1.sort_order < item2.sort_order