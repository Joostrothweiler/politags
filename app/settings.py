# Application settings
APP_NAME = "Politags web app"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME

# At what threshold do we insert a linking
NED_CUTOFF_THRESHOLD = 0.3