# never, ever use DEBUG in production
FLASK_DEBUG = True
DEBUG = True

APPLICATION_ROOT = '/cuts'
LOG_LEVEL = 'INFO'  # CRITICAL / ERROR / WARNING / INFO / DEBUG

# SERVER_NAME = 'localhost:8000'
SECRET_KEY = 'insecurekeyfordevel'

# Image service
CUTOUTS_DIR = '/vos/cutouts'
CUTOUTS_MODE = 'trim'
FITS_MIME_TYPE = 'image/fits'
IMAGES_DIR = '/vos/images'
IMAGE_EXTS = [ 'fits', 'fits.gz' ]

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@vos_redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@vos_redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5
