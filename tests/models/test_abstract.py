import pytest
from oy.models.abstract import (
    Displayable,
    Slugged,
    Titled,
    TimeStampped,
    Publishable,
    Metadata,
)

__install_fixtures__ = False


def concrete_model(cls_name, bases, d, db):
    bases = list(bases) + [db.Model]
    attrs = dict(
        id=db.Column(db.Integer, primary_key=True), __tablename__=cls_name.lower()
    )
    attrs.update(d)
    model = type(cls_name, tuple(bases), attrs)
    db.create_all()
    return model


def test_slugging(app, db):
    slugged = concrete_model(
        "SlugTest", (Slugged, Titled), {"__slugcolumn__": "title"}, db
    )
    s1 = slugged(title=u"ok", slug=u"a-slug")
    db.session.add(s1)
    db.session.commit()
    assert not app.config["ALLWAYS_UPDATE_SLUGS"]
    assert s1.title == u"ok"
    assert s1.slug == u"a-slug"
    s2 = slugged(title=u"A Post")
    db.session.add(s2)
    db.session.commit()
    assert s2.title == u"A Post"
    assert s2.slug == u"a-post"
    app.config["ALLWAYS_UPDATE_SLUGS"] = True
    s1.title = u"Mushy"
    db.session.commit()
    assert s1.slug == u"mushy"


def test_timestammped(db):
    timestampped = concrete_model("TimeStammped", (TimeStampped, Titled), {}, db)
    t = timestampped(title=u"Mushy")
    db.session.add(t)
    db.session.commit()
    assert t.created
    assert not t.updated
    t.title = u"That"
    db.session.commit()
    assert t.updated


def test_metadata(app, db):
    class Content(Titled):
        __keywordscolumn__ = "title"
        __metatitle_column__ = "title"
        __metadescription_column__ = "body"
        body = db.Column(db.UnicodeText)

    metadata = concrete_model("MetaData", (Content, Metadata), {}, db)
    m = metadata(title=u"A Post", body=u"The best post in the known universe")
    assert m.should_auto_generate == True
    db.session.add(m)
    db.session.commit()
    assert m.keywords == "A Post"
    assert m.meta_title == m.title
    assert m.meta_description == m.body
