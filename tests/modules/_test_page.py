from starlit.modules.page.models import Page



def test_page(client, db, user):
    p = Page(title=u'My Page', content=u'A greate content')
    db.session.add(p)
    db.session.commit()
    res = client.get('/my-page')
    assert res.status_code == 200
    assert p.title in res.data
    p1 = Page(title=u'1', content=u'thanks')
    p2 = Page(title=u'2', content=u'thanks')
    p1.parent= p
    p2.parent = p1
    db.session.add_all([p1, p2])
    db.session.commit()
    res = client.get('/my-page/1/2')
    assert res.status_code == 200
    assert p2.title in res.data
