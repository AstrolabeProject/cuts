import os

from flask import abort, jsonify, send_file

from cuts.app import create_celery_app
from config.settings import IMAGES_DIR, IMAGE_EXTS

celery = create_celery_app()


@celery.task()
def make_cutout(image, ra, dec, size):
    return None


@celery.task()
def list_images():
    fyls = [ fyl for fyl in os.listdir(IMAGES_DIR) if (fyl.endswith(tuple(IMAGE_EXTS))) ]
    return jsonify(fyls)


@celery.task()
def send_image(name):
    filename = "{0}/{1}".format(IMAGES_DIR, name)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        return send_file(filename, mimetype='application/fits')
    abort(404)
