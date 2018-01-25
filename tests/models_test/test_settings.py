import pytest
from starlit.modules.core.models import Site
from starlit.modules.editable_settings.models import Settings


def test_settings(db):
    site = Site(name=u'Amam')
    db.session.add(site)
    db.session.commit()
    assert site.settings is not None
    assert site.settings['title'] == u'Starlit CMS'
