from flask import current_app
from werkzeug.local import LocalProxy
from starlit.boot.exts.sqla import db
from starlit.wrappers import StarlitModule


editable_settings = StarlitModule(__name__, 'editable_settings')


class Settings(object):
    def __init__(self, source):
        self.source = source

    def __getattr__(self, key):
        if key in self.source:
            return self.source[key]
        else:
            raise AttributeError("Setting %s does not exists" %key)

    def edit(self, key, value):
        assert key in self.source, "Setting %s does not exists" %key
        self.source[key] = value
        db.session.commit()


def get_active_site():
    from starlit.modules.core.models import Site
    active_site = Site.query.filter(Site.is_active==True).one()
    return active_site

current_site = LocalProxy(lambda: get_active_site())
current_settings = LocalProxy(lambda: Settings(get_active_site().settings))


@editable_settings.app_context_processor
def inject_site():
    return dict(
        site=current_site,
        settings=current_settings
    )
