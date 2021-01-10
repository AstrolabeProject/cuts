# never, ever use DEBUG in production
FLASK_DEBUG = True
DEBUG = True

LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

SECRET_KEY = 'insecurekeyfordevel'


# Name of the application
APP_NAME = 'cuts'

# Path to the root location of the application. When app is run inside
# a container (the default) this is container-relative (e.g. '/cuts')
APP_ROOT = "/{}".format(APP_NAME)

# Configuration directory, inside the application
CONFIG_DIR = "{}/config".format(APP_ROOT)

# Default config file for database configuration.
DEFAULT_DBCONFIG_FILEPATH = "{}/jwst-dbconfig.ini".format(CONFIG_DIR)

# Default schema and table name in which to store image metadata in a database.
DEFAULT_METADATA_TABLE_NAME = 'jwst'

# Default hybrid schema and table name in which to store image metadata in a database.
DEFAULT_HYBRID_TABLE_NAME = 'hybrid'

# List of required SQL fields in the hybrid PG/JSON database table (excluding JSON fields):
SQL_FIELDS_HYBRID = [ 's_dec', 's_ra', 'obs_collection', 'is_public' ]


#
# Celery worker service
#
CELERY_BROKER_URL = 'redis://:devpassword@vos_redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@vos_redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5
