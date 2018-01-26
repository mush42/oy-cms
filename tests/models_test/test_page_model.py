import pytest
from starlit.modules.page.models import Page

def test_basic_page(db, user):
    page = Page(title=u'A Page', content=u'a content', author_id=user.id)
    db.session.add(page)
    db.session.commit()
    page = Page.query.one()
    # Basic assertions
    assert page in Page.query.all()
    assert page.slug == 'a-page'
    # is the page published
    assert page.title == Page.query.published.one().title
    # is the page viewable
    assert page.title == Page.query.viewable.one().title
    # slug path for this page
    assert page.slug_path == 'a-page'
    # now change those probs and see
    page.must_show_in_menu = False
    db.session.commit()
    assert not Page.query.viewable.all()
    page.status = 'draft'
    db.session.commit()
    assert not Page.query.published.all()

def test_parent_child_relation(db, user):
    parent = Page(title=u'Parent', content=u'Parent content.', author_id=user.id)
    child = Page(title=u'child', content=u'Child content.', author_id=user.id)
    parent.children.append(child)
    db.session.add(parent)
    db.session.add(child)
    db.session.commit()
    child = Page.query.get(child.id)
    assert parent.slug_path == 'parent'
    assert child.slug_path == 'parent/child'
    child2 = Page(title=u'Child2', content=u'C2 content.', author_id=user.id)
    child.children.append(child2)
    child3 = Page(title=u'Child3', content=u'Child 3 content.', author_id=user.id)
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
    