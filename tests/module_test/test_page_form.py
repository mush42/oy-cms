from starlit.modules.form.models import Form


def test_form_post_success(client, db):
    res = client.get('/contact-us/')
    assert res.status_code == 200
    assert '<h1>Contact Us</h1>' in res.text
    form = res.forms['contact-us']
    submission = dict(
        name="Foo Bar",
        email="foo@bar.spam",
        subject_type="sales",
        should_reply=True,
        message="Just testing."
    )
    for fname, fval in submission.items():
        form.fields[fname][0].value = fval
    fres = form.submit().follow()
    assert fres.status_code == 200
    assert 'Thanks a bundle' in fres.text
    dbform = Form.query.one()
    assert dbform.entries[0]
    assert dbform.entries[0].fields[0].value == submission['name']
