# Environment variables for the application boycott
[% set PROJECT_NAME = project_name|upper %]
# Universal stuff
[[ PROJECT_NAME ]]_DEBUG = True
[[ PROJECT_NAME ]]_SECRET_KEY = "[[ secret_key ]]"
[[ PROJECT_NAME ]]_DB_URI = 'sqlite:///db.sqlite'
[[ PROJECT_NAME ]]_PASSWORD_SALT = "[[ password_sult ]]"

# Flask-specific stuff
FLASK_APP=[[ project_name ]]:app
FLASK_ENV = 'development'
FLASK_DEBUG= True