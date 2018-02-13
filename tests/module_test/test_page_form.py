
def test_form_post_success(client, db):
    res = client.get('/contact-us/')
    assert res.status_code == 200
    assert '.' in res.text


