import pytest
from oy.models.abstract.slugged import Titled, Slugged, ScopedUniquelySlugged, MPSlugged
from oy.models.abstract.misc import SelfRelated



def test_slugged(app, db, makemodel):
    slugged = makemodel("Slugged", (Slugged, Titled), d={"__slugcolumn__": "title"})
    s1 = slugged(title="Just Testing", slug="a-slug")
    db.session.add(s1)
    db.session.commit()
    assert s1.slug == "a-slug"
    s2 = slugged(title="Hello")
    db.session.add(s2)
    db.session.commit()
    assert s2.slug == "hello"


def test_scoped_slugged(db, makemodel):
    Scoped = makemodel("ScopedSlugged", (ScopedUniquelySlugged, Titled, SelfRelated))
    sc1 = Scoped(title="Hello")
    db.session.add(sc1)
    db.session.commit()
    assert sc1.slug == 'hello'
    sc2 = Scoped(title="Hello")
    db.session.add(sc2)
    db.session.commit()
    assert sc2.slug == 'hello-1'
    sc3 = Scoped(title="Hello")
    sc4 = Scoped(title="Hello")
    db.session.add_all((sc3, sc4,))
    db.session.commit()
    assert sc3.slug == 'hello-2'
    assert sc4.slug == 'hello-3'
    parent = Scoped(title="Parent")
    child1 = Scoped(title="Child")
    db.session.add(child1)
    parent.children.append(child1)
    db.session.commit()
    assert child1.slug == 'child'
    child2 = Scoped(title="Child", parent=parent)
    db.session.add(child2)
    db.session.commit()
    assert child2.slug == 'child-1'
    toplevel = Scoped(title="Child")
    db.session.add(toplevel)
    db.session.commit()
    assert toplevel.slug == "child"


def test_mp_slugged(db, makemodel):
    MPS = makemodel("MPSluggedTest", (Titled, ScopedUniquelySlugged, MPSlugged, SelfRelated,))
    parent = MPS(title="parent")
    child_level1 = MPS(title="Child")
    child_level2 = MPS(title="Sub Child")
    child_level1.parent = parent
    child_level2.parent = child_level1
    db.session.add_all((parent, child_level1, child_level2,))
    db.session.commit()
    assert parent.slug_path == "parent"
    assert child_level1.slug_path == "parent/child"
    assert child_level2.slug_path == "parent/child/sub-child"
    child_level2.parent = parent
    db.session.commit()
    assert child_level2.slug_path == "parent/sub-child"
    another_child = MPS(title="another")
    parent.children.append(another_child)
    db.session.add(another_child)
    db.session.commit()
    assert another_child.slug_path == "parent/another"
