import pytest
from werkzeug.exceptions import NotFound
from oy.models.page import Page
from oy.views import ContentView


class CustomePageView(ContentView):
    def serve(self):
        return {}

    def serve(self):
        return self.page.title

def test_view_basic(app, client, db, makemodel):
    idcol = db.Column(db.Integer, db.ForeignKey(Page.id), primary_key=True)
    contype = 'custom_page'
    CustomPage = makemodel("CustomePage", (Page,), d={
        "id": idcol,
        "__contenttype__": contype,
    })
    cust = CustomPage(title="Hello", author_id=1)
    db.session.add(cust)
    db.session.commit()
    resp = client.get(cust.url, status=404)
    app.add_contenttype_handler("custom_page", CustomePageView)
    resp = client.get(cust.url)
    assert resp.status == '200 OK'
    assert "Hello" in resp.text
    class CustomPageMiddleware:
        def process_response(self, response, handler):
            assert response == "Hello"
            return "Custom"
    app.apply_middleware("custom_page", CustomPageMiddleware)
    resp = client.get(cust.url)
    assert resp.status == '200 OK'
    assert "Custom" in resp.text
