import os

from flask import abort, jsonify, send_file

from cuts.app import create_celery_app
from config.settings import IMAGES_DIR, IMAGE_EXTS

celery = create_celery_app()


@celery.task()
def list_images ():
    image_files = list_image_files()
    return jsonify(image_files)


@celery.task()
def fetch_image (name):
    filename = "{0}/{1}".format(IMAGES_DIR, name)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        return send_file(filename, mimetype='application/fits')
    abort(404)


@celery.task()
def get_astrocut_cutout (args):
    filename = fetch_horsehead(args)
    return send_file(filename, mimetype='application/fits')



# internal helper methods
#
def list_image_files (imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    return [ fyl for fyl in os.listdir(imageDir) if (fyl.endswith(tuple(extents))) ]

def fetch_horsehead (args):
    # TODO: IMPLEMENT LATER. For now, send same file.
    filename = "{0}/{1}".format(IMAGES_DIR, 'HorseHead.fits')
    return filename
