import pytest
from starlit.modules.editable_settings.models import SettingsProfile


def test_settings(db):
    sp = SettingsProfile.query.get(1)
    assert sp.settings is not None
    assert sp.settings['title'] == u'Starlit CMS'
