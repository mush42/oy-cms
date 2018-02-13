
def test_index_will_return_a_response(client, db):
    res = client.get('/')
    assert res.status_code == 200
    assert 'Wellcome' in res.text


def test_other_pages_work_too(client, db):
    res = client.get('/services')
    assert res.status_code == 200
    assert 'Our Services' in res.text


def test_nested_pages_could_be_accessed(client, db):
    res = client.get('/services/design/')
    assert res.status_code == 200
    assert 'Our Design' in res.text
    