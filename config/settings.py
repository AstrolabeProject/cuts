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

# Root directory for the data directory tree.
DATA_ROOT = '/usr/local/data/vos'

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
CELERY_BROKER_URL = 'redis://:devpassword@redis:6379/0'
result_backend = 'redis://:devpassword@redis:6379/0'
accept_content = ['json']
task_serializer = 'json'
result_serializer = 'json'
redis_max_connections = 5
