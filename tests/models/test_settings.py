import pytest
from starlit.models.settings import SettingsProfile


def test_settings(db):
    sp = SettingsProfile.query.get(1)
    assert sp.settings is not None
    assert sp.settings['title'] == u'Starlit CMS'
