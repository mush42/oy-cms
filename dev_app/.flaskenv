# Environment variables for the application boycott

# Universal stuff
DEV_APP_DEBUG = True
DEV_APP_SECRET_KEY = "f99f39e15ecb038cb9bb877437769bed88bfd060318cbca830d070884fc6315b"
DEV_APP_DB_URI = 'sqlite:///db.sqlite'
DEV_APP_PASSWORD_SALT = "f3f266c2e517bac01c9a5b648b770eebf790d34cb4f7dcabe81dcfa564995303"

# Flask-specific stuff
FLASK_APP=dev_app:app
FLASK_ENV = 'development'
FLASK_DEBUG= True