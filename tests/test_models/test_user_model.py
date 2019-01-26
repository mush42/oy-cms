import pytest
from oy.models import User


def test_add_user(db):
    user = User.query.get(1)
    assert user.active
