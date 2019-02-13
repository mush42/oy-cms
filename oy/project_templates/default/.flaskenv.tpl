# Environment variables for project  [[ project_name ]]
[% set PROJECT_NAME = project_name|upper %]
# Basic environment variables
[[ PROJECT_NAME ]]_DEBUG=True
[[ PROJECT_NAME ]]_SECRET_KEY="[[ secret_key ]]"
[[ PROJECT_NAME ]]_DB_URI="sqlite:///db.sqlite"
[[ PROJECT_NAME ]]_PASSWORD_SALT="[[ password_sult ]]"

# Flask-specific environment variables
FLASK_APP="[[ project_name ]]:create_app"
FLASK_ENV=development
FLASK_DEBUG=True