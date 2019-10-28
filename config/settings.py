# never, ever use DEBUG in production
DEBUG = True

SECRET_KEY = 'insecurekeyfordevel'

# Image service
CUTOUTS_DIR = '/vos/cutouts'
CUTOUTS_LIB = 'astropy'
CUTOUTS_MODE = 'trim'
IMAGES_DIR = '/vos/images'
IMAGE_EXTS = [ 'fits', 'fits.gz' ]

# Celery.
CELERY_BROKER_URL = 'redis://:devpassword@vos_redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://:devpassword@vos_redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_REDIS_MAX_CONNECTIONS = 5
