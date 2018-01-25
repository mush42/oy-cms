import pytest
from starlit.modules.core.models import Site

def test_basic_site(db):
    site = Site(name=u'sparse site')
    db.session.add(site)
    db.session.commit()
    assert Site.query.first() == site

def test_only_one_site_is_active_at_the_time(db):
    site1 = Site(name=u'Site1', is_active=True)
    db.session.add(site1)
    db.session.commit()
    assert site1.is_active
    site2 = Site(name=u'Site2', is_active=True)
    db.session.add(site2)
    db.session.commit()
    assert site2.is_active
    assert not site1.is_active
