#-*-coding: utf-8-*-

# This file is used to generate the render context to
# be used in the rendering of other files in this project
# It will be deleted from the final output folder

import os

__all__ = ['secret_key', 'db_uri', 'password_sult']


secret_key = os.urandom(24).hex()
db_uri = 'db.sqlite'
password_sult = os.urandom(24).hex()
