import pytest
from oy.contrib.bootstrap4 import Bootstrap4
from oy.contrib.redirects import Redirects 


def test_contrib_exts(app):
    bs4 = Bootstrap4(app)

    # Should fail if attempting to register the same ext twice
    with pytest.raises(RuntimeError):
        Bootstrap4(app)
    assert bs4.name in app.modules
    assert bs4.name in app.data["_oy_contrib_extensions"]

    # registering an extention without module_args should succeed
    red = Redirects(app)
    assert red.name in app.data["_oy_contrib_extensions"]
    assert red.name not in app.modules
