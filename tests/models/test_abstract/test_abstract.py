import pytest
from oy.models.abstract import TimeStampped, Publishable, Metadata, Titled


def test_timestammped(db, makemodel):
    timestampped = makemodel("TimeStampped", (TimeStampped, Titled))
    t = timestampped(title=u"Mushy")
    db.session.add(t)
    db.session.commit()
    assert t.created
    assert not t.updated
    t.title = u"That"
    db.session.commit()
    assert t.updated


def test_metadata(app, db, makemodel):
    class Content(Titled):
        __keywordscolumn__ = "title"
        __metatitle_column__ = "title"
        __metadescription_column__ = "body"
        body = db.Column(db.UnicodeText)

    metadata = makemodel("MetadataModel", (Content, Metadata))
    m = metadata(title=u"A Post", body=u"The best post in the known universe")
    assert m.should_auto_generate == True
    db.session.add(m)
    db.session.commit()
    assert m.keywords == "A Post"
    assert m.meta_title == m.title
    assert m.meta_description == m.body
