import pytest
from oy.models import Page
from oy.contrib.redirects import Redirects, RedirectModel


def test_basic_redirects(app, client, db):
    Redirects(app)

    @app.route("/reachable")
    def reachable():
        return "You reached here"

    @app.route("/never-reached")
    def never_reached():
        return "You shouldn't reach here"

    resp = client.get("/never-reached")
    assert resp.status == "200 OK"

    redirect = RedirectModel(
        from_url="/never-reached",
        to_url="/reachable",
        permanent=True)
    db.session.add(redirect)
    db.session.commit()

    resp = client.get("/never-reached", status=301)
    assert resp.status == "301 MOVED PERMANENTLY"
    resolved = resp.follow()
    assert "You reached here" in resolved.text

    redirect.permanent = False
    db.session.commit()

    resp = client.get("/never-reached", status=307)
    assert resp.status == "307 TEMPORARY REDIRECT"


def test_redirects_with_page(app, client, db):
    Redirects(app)

    @app.route("/not-reachable")
    def never_reached():
        return "You shouldn't reach here"

    to_page = Page(title="The Reachable Page")
    db.session.add(to_page)
    db.session.commit()

    @app.contenttype_handler("page")
    def page_handler():
        return "Wellcome to page"

    resp = client.get("/not-reachable", status=200)
    assert resp.status == "200 OK"
    assert "You shouldn't reach here" in resp.text

    redirect = RedirectModel(from_url="/not-reachable", to_page=to_page)
    db.session.add(redirect)
    db.session.commit()

    respage = client.get("/not-reachable", status=307)
    assert respage.status == "307 TEMPORARY REDIRECT"
    resolved = respage.follow()
    assert "Wellcome to page" in resolved.text
