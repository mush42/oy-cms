import pytest
import time
from oy.models.mixins import TimeStampped, Metadata, Titled


def test_timestammped(app, db, makemodel):
    TStampped = makemodel("TimeStampped", (TimeStampped, Titled))
    t = TStampped(title=u"Mushy")
    db.session.add(t)
    db.session.commit()
    assert t.created
    assert t.updated
    first_updated = t.updated
    time.sleep(0.1)
    with app.test_request_context():
        t.title = u"That"
        db.session.commit()
    assert t.updated > first_updated


def test_metadata(app, db, makemodel):
    class Content(Titled):
        body = db.Column(db.UnicodeText)

        def __get_meta_title__(self):
            return "A Post"

        def __get_meta_description__(self):
            return "The best post in the known universe"

        def __get_keywords__(self):
            return "post, article, great"

    metadata = makemodel("MetadataModel", (Content, Metadata))
    m = metadata(title="A Post", body="The best post in the known universe")
    db.session.add(m)
    db.session.commit()
    assert m.should_auto_generate == True
    assert m.keywords == "post, article, great"
    assert m.meta_title == m.title
    assert m.meta_description == m.body
