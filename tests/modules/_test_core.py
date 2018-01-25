from starlit.modules.core.models.site import Site


def test_site_api(client, app, db, user):
    s = Site(name=u'My Site')
    db.session.add(s)
    db.session.commit()
    assert 'api' in app.config['ENABLED_FEATURES']
    res = client.get('/api/sites/')
    assert res.status_code == 200
    assert s.name in res.data