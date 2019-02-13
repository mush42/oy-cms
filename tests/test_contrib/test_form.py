import pytest
from oy import page_url
from oy.contrib.form import Form as FormExt
from oy.contrib.form.models import Form
from oy.contrib.bootstrap4 import Bootstrap4
from oy.contrib.demo_content import FixtureInstaller, DemoContent


def test_basic_form(app, client, db):
    Bootstrap4(app)
    FixtureInstaller(DemoContent(app)).install()
    FixtureInstaller(FormExt(app)).install()

    form = Form.query.first()

    resp = client.get(page_url(form))
    pform = resp.forms[form.slug]
    pform["name"] = "Spam"
    pform["email"] = "foo@bar.spam"
    pform["message"] = "Hello there."
    post = pform.submit()
    assert post.status_code == 302
