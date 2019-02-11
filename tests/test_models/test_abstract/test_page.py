import pytest
from oy.models.abstract import AbstractPage



def test_page_imp(db, makemodel):
    BasePage = makemodel("BasePage", (AbstractPage,), dict(
        __mapper_args__={"polymorphic_identity": "base-page"}
    ))
    parent = BasePage(title="Parent")
    child1 = BasePage(title="Child 1", parent=parent)
    child2= BasePage(title="Child 2", parent=parent)
    subchild1 = BasePage(title="SubChild 1", parent=child1)
    subsubchild1 = BasePage(title="SubSubChild 1", parent=subchild1)
    pages = [parent, child1, child2, subchild1, subsubchild1]
    db.session.add_all(pages)
    db.session.commit()
    check = lambda p: AbstractPage.construct_url_path(p) == p.url_path
    assert all(check(p) for p in pages)
    child1.move_inside(child2.id)
    db.session.commit()
    assert all(check(p) for p in pages)
    child1.move_inside(parent.id)
    db.session.commit()
    assert all(check(p) for p in pages)
    subchild1.move_inside(child2.id)
    db.session.commit()
    assert all(check(p) for p in pages)
    subsubchild1.move_after(child1.id)
    db.session.commit()
    assert all(check(p) for p in pages)
