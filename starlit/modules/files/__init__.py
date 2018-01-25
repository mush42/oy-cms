from flask import current_app, send_from_directory
from starlit.wrappers import StarlitModule

files = StarlitModule(__name__, 'files')

@files.route('/files/<path:filename>', endpoint='files')
def serve_file(filename):
    return send_from_directory(current_app.config['UPLOADS_PATH'], filename)
