import pytest
from starlit.modules.page.models import Page

def test_basic_page(db):
    page = Page(title=u'A Page', content=u'a content')
    db.session.add(page)
    db.session.commit()
    # Basic assertions
    assert page in Page.query.all()
    assert page.slug == 'a-page'
    # is the page published
    assert page in Page.query.published.all()
    # is the page viewable
    assert page in Page.query.viewable.all()
    # slug path for this page
    assert page.slug_path == 'a-page'
    # now change those probs and see
    page.is_live = False
    db.session.commit()
    assert page not in Page.query.viewable.all()
    page.status = 'draft'
    db.session.commit()
    assert page not in Page.query.published.all()

def test_parent_child_relation(db):
    parent = Page(title=u'Parent', content=u'Parent content.')
    child = Page(title=u'child', content=u'Child content.')
    parent.children.append(child)
    db.session.add(parent)
    db.session.add(child)
    db.session.commit()
    child = Page.query.get(child.id)
    assert parent.slug_path == 'parent'
    assert child.slug_path == 'parent/child'
    child2 = Page(title=u'Child2', content=u'C2 content.')
    child.children.append(child2)
    child3 = Page(title=u'Child3', content=u'Child 3 content.')
    child3.parent = child2
    db.session.add(child)
    db.session.add(child2)
    db.session.add(child3)
    db.session.commit()
    assert child2.slug_path == 'parent/child/child2'
    assert child3.slug_path == 'parent/child/child2/child3'
    parent.children.append(child2)
    child2.slug = u'mychild2'
    db.session.commit()
    assert len(child.children)==0
    assert child3.slug_path == 'parent/mychild2/child3'
