# Application settings
APP_NAME = "Politags web app"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME

# At what threshold do we RETURN a linking in the API. Linkings are always stored.
# We may want to create a separate persons and parties cutoff.
NED_CUTOFF_THRESHOLD = 0.75