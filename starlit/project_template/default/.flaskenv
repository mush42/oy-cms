# Environment variables for the application boycott
{% set PROJECT_NAME = project_name|upper %}
# Universal stuff
{{ PROJECT_NAME }}_DEBUG=1
{{ PROJECT_NAME }}_SECRET_KEY = ''a5792b96c6c84f1da10396f8d34d234b''
{{ PROJECT_NAME }}_DB_URI = 'sqlite:///db.sqlite'
{{ PROJECT_NAME }}_PASSWORD_SALT = 'Aq6V28444baff40e885fa807f45ed454a'

# Flask-specific stuff
FLASK_APP={{ project_name }}:app
FLASK_ENV = 'development'
FLASK_DEBUG=${{ PROJECT_NAME }}_DEBUG
