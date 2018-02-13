import pytest
from starlit.modules.core.models import User


def test_add_user(db):
    user = User.query.get(1)
    assert user.active
    