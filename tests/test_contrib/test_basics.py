import pytest
from oy.contrib.extbase import OyExtBase
from oy.contrib.bootstrap4 import Bootstrap4


def test_contrib_exts(app):
    bs4 = Bootstrap4(app)

    # Should fail if attempting to register the same ext twice
    with pytest.raises(RuntimeError):
        Bootstrap4(app)
    assert bs4.name in app.modules
    assert bs4.name in app.data["_oy_contrib_extensions"]

    # Registering exts without module_args should work
    class TestExt(OyExtBase):
        name = "test-ext"

    tes = TestExt(app)
    assert tes.name in app.data["_oy_contrib_extensions"]
    assert tes.name not in app.modules
