# Environment variables for the application boycott

# Universal stuff
DEV_APP_DEBUG = True
DEV_APP_SECRET_KEY = 'a5792b96c6c84f1da10396f8d34d234b'
DEV_APP_DB_URI = 'sqlite:///db.sqlite'
DEV_APP_PASSWORD_SALT = 'Aq6V28444baff40e885fa807f45ed454a'

# Flask-specific stuff
FLASK_APP=dev_app:app
FLASK_ENV = 'development'
FLASK_DEBUG= True