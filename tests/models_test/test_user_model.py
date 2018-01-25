import pytest
from starlit.boot.exts.security import user_datastore


def test_add_user(db):
    user = user_datastore.create_user(
        user_name=u'admin',
        password=u'admin',
        email=u'admin@localhost')
    db.session.add(user)
    db.session.commit()