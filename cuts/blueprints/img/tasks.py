import os

from flask import abort, current_app, jsonify, request, send_file, send_from_directory

from cuts.app import create_celery_app
from config.settings import CUTOUTS_DIR, CUTOUTS_MODE, IMAGES_DIR, IMAGE_EXTS

from astrocut import fits_cut

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError, PartialOverlapError
from astropy.wcs import WCS


# Instantiate the Celery client appication
celery = create_celery_app()

FITS_MIME_TYPE = "image/fits"

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
        return send_from_directory(IMAGES_DIR, name, mimetype=FITS_MIME_TYPE,
                                   as_attachment=True, attachment_filename=name)
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
        return send_from_directory(CUTOUTS_DIR, name, mimetype=FITS_MIME_TYPE,
                                   as_attachment=True, attachment_filename=name)
    abort(404)


@celery.task()
def get_astrocut_cutout (args):
    co_args = parse_cutout_args(args)

    # figure out which image to make cutout from
    imagePath = find_image(co_args)
    if (not imagePath):
        abort(404)

    # cutouts should be written to the cutouts directory but fails due to an Astrocut bug
    co_files = fits_cut([imagePath], co_args['center'], co_args['co_size'],
                        single_outfile=False, output_dir=CUTOUTS_DIR)

    # create a return filename and return file
    co_filename = make_ac_cutout_filename(co_files[0], co_args)
    return send_file(co_files[0], mimetype=FITS_MIME_TYPE,
                     as_attachment=True, attachment_filename=co_filename)



@celery.task()
def get_astropy_cutout (args):
    co_args = parse_cutout_args(args)

    # figure out which image to make cutout from
    imagePath = find_image(co_args)
    if (not imagePath):
        abort(404)

    hdu = fits.open(imagePath)[0]
    wcs = WCS(hdu.header)

    # make the cutout, including the WCS info
    try:
        cutout = Cutout2D(hdu.data, position=co_args['center'], size=co_args['co_size'],
                          wcs=wcs, mode=CUTOUTS_MODE)
    except (NoOverlapError, PartialOverlapError):
        abort(400)

    # save cutout image in the FITS HDU and update FITS header with cutout WCS
    hdu.data = cutout.data
    hdu.header.update(cutout.wcs.to_header())

    # write the cutout to a new FITS file
    co_filename = make_cutout_filename(imagePath, cutout, co_args)
    co_filepath = make_cutout_filepath(co_filename)
    hdu.writeto(co_filepath, overwrite=True)

    return send_file(co_filepath, mimetype=FITS_MIME_TYPE,
                     as_attachment=True, attachment_filename=co_filename)


#
# Internal helper methods
#

# Return a list of filenames for FITS files in the given directory.
# FITS files are identified by the given list of valid file extensions.
def list_fits_files (imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    return [ fyl for fyl in os.listdir(imageDir) if (fyl.endswith(tuple(extents))) ]


# Return a filename for the Astrocut cutout from info in the given parameters
def make_ac_cutout_filename (imagePath, co_args):
    baseName = os.path.splitext(os.path.basename(imagePath))[0]
    ra = co_args['ra']
    dec = co_args['dec']
    size = co_args['sizeDeg']
    return "{0}_{1}_{2}_{3}x{4}_astrocut.fits".format(baseName, ra, dec, size, size)

# Return a filename for the Astropy cutout from info in the given parameters
def make_cutout_filename (imagePath, cutout, co_args):
    baseName = os.path.splitext(os.path.basename(imagePath))[0]
    ra = co_args['ra']
    dec = co_args['dec']
    shape = cutout.shape
    return "{0}__{1}_{2}_{3}x{4}.fits".format(baseName, ra, dec, shape[0], shape[1])

# Return a filepath for the given filename in the cutout cache area
def make_cutout_filepath (filename, cutout_dir=CUTOUTS_DIR):
    return "{0}/{1}".format(cutout_dir, filename)


# Parse, convert, and check the given arguments, returning a dictionary of cutout arguments.
# Any arguments needed by cutout routines should be passed through to the return dictionary.
def parse_cutout_args (args):
    co_args = {}                            # result dictionary

    raStr = args.get("ra")
    if (not raStr):
        abort(400)
    else:
        ra = float(raStr)
        co_args['ra'] = ra

    decStr = args.get("dec")
    if (not decStr):
        abort(400)
    else:
        dec = float(decStr)
        co_args['dec'] = dec

    co_args['center'] = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

    filt = args.get("filter")
    if (not filt):
        abort(400)
    else:
        co_args['filter'] = filt

    sizeStr = args.get("size")
    if (not sizeStr):
        sizeStr = args.get("sizeDeg")
    if (not sizeStr):
        abort(400)
    sizeDeg = float(sizeStr)
    co_args['sizeDeg'] = sizeDeg
    co_args['co_size'] = u.Quantity(sizeDeg, u.degree) # make scalar Quantity

    sizeArcMinStr = args.get("sizeArcMin")
    if (sizeArcMinStr):
        co_args['sizeArcMin'] = float(sizeArcMinStr)

    sizeArcSecStr = args.get("sizeArcSec")
    if (sizeArcSecStr):
        co_args['sizeArcSec'] = float(sizeArcSecStr)

    return co_args                          # return parsed, converted cutout arguments


def fetch_horsehead (args):
    # TODO: IMPLEMENT LATER. For now, send same file.
    filename = "{0}/{1}".format(IMAGES_DIR, "HorseHead.fits")
    return filename


# return an image from the image directory selected by the given cutout args
def find_image (co_args):
    fyls = {
        "F090W": "goods_s_F090W_2018_08_29.fits",
        "F115W": "goods_s_F115W_2018_08_29.fits",
        "F150W": "goods_s_F150W_2018_08_29.fits",
        "F200W": "goods_s_F200W_2018_08_29.fits",
        "F277W": "goods_s_F277W_2018_08_29.fits",
        "F335M": "goods_s_F335M_2018_08_29.fits",
        "F356W": "goods_s_F356W_2018_08_30.fits",
        "F410M": "goods_s_F410M_2018_08_30.fits",
        "F444W": "goods_s_F444W_2018_08_31.fits"
    }

    # currently, selecting one image based on filter type
    selected = fyls.get(co_args.get('filter'))
    if (not selected):
        return None

    return os.path.join(IMAGES_DIR, selected)
