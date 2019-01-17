import pytest
from oy.models.abstract.misc import SelfRelated, Orderable



def test_self_related(db, makemodel):

    class SelfRel(SelfRelated, db.Model):
        id = db.Column(db.Integer, primary_key=True)
        type = db.Column(db.String(50))

        __mapper_args__ = {
            "polymorphic_identity": "base_type",
            "polymorphic_on": type
        }

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


def test_orderable(db, makemodel):
    Ord = makemodel("Ord", (SelfRelated, Orderable,))
    top1 = Ord()
    top2 = Ord(_sort_order=11)
    db.session.add_all((top1, top2,))
    db.session.commit()
    assert top1.sort_order == top1.id
    assert top2.sort_order == top2.id
    with pytest.raises(RuntimeError):
        erord = Ord()
        erord.sort_order = 22
    t1ord, t2ord = [t.sort_order for t in (top1, top2)]
    top1.sort_order = t2ord
    db.session.commit()
    assert top1.sort_order == t2ord
    assert top2.sort_order > t2ord
