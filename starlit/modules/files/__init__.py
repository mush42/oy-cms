from flask import current_app, send_from_directory
from starlit.wrappers import StarlitModule
from .models import *


files = StarlitModule('files', __name__, builtin=True)


def serve_file(filename, path=None):
    path = path or current_app.config['UPLOADS_PATH']
    return send_from_directory(path, filename)

@files.after_setup
def add_file_serving_root(app):
    url_prefix = app.config.get('FILES_URL_PREFIX', '`files')
    app.add_url_rule('/{}/<path:filename>'.format(url_prefix), 'serve_file', 'serve_file')

