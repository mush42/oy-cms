import pytest
from starlit.modules.editable_settings.models import SettingsProfile


def test_settings(db):
    sp = SettingsProfile(name=u'Test Settings Profile')
    db.session.add(sp)
    db.session.commit()
    assert sp.settings is not None
    assert sp.settings['title'] == u'Starlit CMS'
