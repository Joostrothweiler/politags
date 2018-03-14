import os

# *****************************
# Environment specific settings
# *****************************

# DO NOT use "DEBUG = True" in production environments
DEBUG = True
PRODUCTION_ENVIRONMENT = False
ALWAYS_PROCESS_ARTICLE_AGAIN = False
LOGGING_LEVEL=logging.INFO

# DO NOT use Unsecure Secrets in production environments
# Generate a safe one with:
#     python -c "import os; print repr(os.urandom(24));"
SECRET_KEY = 'Some secret key'

# SQLAlchemy settings
# Connection
DB_USER = 'someuser'
DB_PASSWORD = 'hispassword'
DB_NAME = 'yourdbname'

SQLALCHEMY_DATABASE_URI = 'postgresql+pygresql://{}:{}@postgres/{}'.format(DB_USER, DB_PASSWORD, DB_NAME)
# Other settings
SQLALCHEMY_TRACK_MODIFICATIONS = False    # Avoids a SQLAlchemy Warning

# POLIFLOW API CREDENTIALS
PFL_USER = 'someuser'
PFL_PASSWORD = 'secretpassword'

