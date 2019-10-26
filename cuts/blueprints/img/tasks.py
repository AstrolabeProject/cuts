import os

from flask import abort, current_app, jsonify, request, send_file

from cuts.app import create_celery_app
from config.settings import CUTOUTS_DIR, IMAGES_DIR, IMAGE_EXTS

from astrocut import fits_cut
from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS


# Instantiate the Celery client appication
celery = create_celery_app()

# logger = current_app.logger                 # TODO: FIX

# Full image methods
#

@celery.task()
def list_images ():
    image_files = list_fits_files()
    return jsonify(image_files)


@celery.task()
def fetch_image (name):
    filename = "{0}/{1}".format(IMAGES_DIR, name)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        return send_file(filename, mimetype="application/fits")
    abort(404)


# Image cutout methods
#

@celery.task()
def list_cutouts ():
    image_files = list_fits_files(imageDir=CUTOUTS_DIR)
    return jsonify(image_files)


@celery.task()
def fetch_cutout (name):
    filename = "{0}/{1}".format(CUTOUTS_DIR, name)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        return send_file(filename, mimetype="application/fits")
    abort(404)


@celery.task()
def get_astrocut_cutout (args):
    # return send_file(fetch_horsehead(args), mimetype="application/fits")
    ra = float(args.get("ra"))
    dec = float(args.get("dec"))
    sizeDeg = float(args.get("sizeDeg"))
    center = SkyCoord(ra=ra*u.degree, dec=dec*u.degree)
    # co_size = [ sizeDeg, sizeDeg ]
    co_size = [ 800, 1000 ]
    fyls = [ "/vos/images/goods_s_F356W_2018_08_30.fits" ] # TODO: IMPLEMENT fetch later

    # logger.error("CUTOUTS_DIR=%s",CUTOUTS_DIR) # REMOVE LATER
#    co_files = fits_cut(fyls, center, co_size, single_outfile=False, cutout_prefix="", output_dir=CUTOUTS_DIR)
    co_files = fits_cut(fyls, center, co_size, single_outfile=False)

    # logger.error("CO_FILES=%s",co_files) # REMOVE LATER

    # filename = fetch_horsehead(args)
    return send_file(co_files[0], mimetype="application/fits")



# Internal helper methods
#
def list_fits_files (imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    return [ fyl for fyl in os.listdir(imageDir) if (fyl.endswith(tuple(extents))) ]

def fetch_horsehead (args):
    # TODO: IMPLEMENT LATER. For now, send same file.
    filename = "{0}/{1}".format(IMAGES_DIR, "HorseHead.fits")
    return filename
