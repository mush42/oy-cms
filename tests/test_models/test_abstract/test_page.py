import pytest
from oy.models import Page


def test_home_page(db):
    home1 = Page(title="Home1", slug="index")
    db.session.add(home1)
    db.session.commit()
    assert home1.slug_path == "index"
    assert home1.is_home
