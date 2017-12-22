# Application settings
APP_NAME = "Politags web app"
APP_SYSTEM_ERROR_SUBJECT_LINE = APP_NAME + " system error"

# Flask-SQLAlchemy settings
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-User settings
USER_APP_NAME = APP_NAME


# NED settings
# Weights should add up to 1.0
NED_STRING_SIM_WEIGHT = 0.9
NED_CONTEXT_SIM_WEIGHT = 0.1
# At what threshold do we insert a linking
NED_CUTOFF_THRESHOLD = 0.3