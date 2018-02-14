import pdb

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
    pdb.set_trace()
    for fname, fval in submission.items():
        form.fields[fname].value = fval
    fres = form.submit()
    assert fres.status_code == 200
    assert 'Thanks a bundle' in fres.text
