import os

from flask import current_app, jsonify, request, send_file, send_from_directory

from cuts.app import create_celery_app
from config.settings import CUTOUTS_DIR, CUTOUTS_MODE, FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS
from cuts.blueprints.img import exceptions

# from astrocut import fits_cut

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError, PartialOverlapError
from astropy.wcs import WCS


# Instantiate the Celery client appication
celery = create_celery_app()


#
# Full image methods
#

@celery.task()
def list_images ():
    image_files = list_fits_files()
    return jsonify(image_files)


@celery.task()
def fetch_image (filename):
    return return_image(filename)


#
# Image cutout methods
#

@celery.task()
def list_cutouts ():
    image_files = list_fits_files(imageDir=CUTOUTS_DIR)
    return jsonify(image_files)


@celery.task()
def fetch_cutout (filename):
    return return_image(filename, imageDir=CUTOUTS_DIR)


# @celery.task()
# def get_astrocut_cutout (args):
#     co_args = parse_cutout_args(args)

#     # figure out which image to make cutout from
#     imagePath = find_image(co_args)
#     if (not imagePath):
#         filt = co_args.get('filter')
#         errMsg = "An image was not found for filter {0} in images directory {1}".format(filt, IMAGES_DIR)
#         current_app.logger.error(errMsg)
#         raise exceptions.RequestException(errMsg)

#     # cutouts should be written to the cutouts directory but fails due to an Astrocut bug
#     co_files = fits_cut([imagePath], co_args['center'], co_args['co_size'],
#                         single_outfile=False, output_dir=CUTOUTS_DIR)

#     # create a return filename and return file
#     co_filename = make_ac_cutout_filename(co_files[0], co_args)
#     return send_file(co_files[0], mimetype=FITS_MIME_TYPE,
#                      as_attachment=True, attachment_filename=co_filename)



@celery.task()
def get_astropy_cutout (args):
    # parse the parameters for the cutout
    co_args = parse_cutout_args(args)

    # figure out which image to make a cutout from based on the cutout parameters
    img_filename = find_image_filename(co_args)
    if (not img_filename):
        filt = co_args.get('filter')
        errMsg = "An image was not found for filter {0} in images directory {1}".format(filt, IMAGES_DIR)
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return return_image(img_filename)   # exit out now, returning entire image

    img_path = make_filepath_from_filename(img_filename)
    hdu = fits.open(img_path)[0]
    wcs = WCS(hdu.header)

    # make the cutout, including the WCS info
    try:
        cutout = Cutout2D(hdu.data, position=co_args['center'], size=co_args['co_size'],
                          wcs=wcs, mode=CUTOUTS_MODE)
    except (NoOverlapError, PartialOverlapError):
        sky = co_args['center']
        errMsg = "There is no overlap between the reference image and the given center coordinate: {0}, {1} {2} ({3})".format(sky.ra.value, sky.dec.value, sky.ra.unit.name, sky.frame.name)
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    # save cutout image in the FITS HDU and update FITS header with cutout WCS
    hdu.data = cutout.data
    hdu.header.update(cutout.wcs.to_header())

    # write the cutout to a new FITS file and then return it
    co_filename = make_cutout_filename(img_filename, cutout, co_args)
    write_cutout(hdu, co_filename)

    return return_image(co_filename, imageDir=CUTOUTS_DIR) # return the cutout image



#
# Internal helper methods
#

# Return a filepath for the given filename in the cutout cache area
def make_filepath_from_filename (filename, imageDir=IMAGES_DIR):
    return os.path.join(imageDir, filename)


# Return a list of filenames for FITS files in the given directory.
# FITS files are identified by the given list of valid file extensions.
def list_fits_files (imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    return [ fyl for fyl in os.listdir(imageDir) if (fyl.endswith(tuple(extents))) ]


# # Return a filename for the Astrocut cutout from info in the given parameters
# def make_ac_cutout_filename (imagePath, co_args):
#     baseName = os.path.splitext(os.path.basename(imagePath))[0]
#     ra = co_args['ra']
#     dec = co_args['dec']
#     size = co_args['size']
#     return "{0}_{1}_{2}_{3}_astrocut.fits".format(baseName, ra, dec, size)


# Return a filename for the Astropy cutout from info in the given parameters
def make_cutout_filename (imagePath, cutout, co_args):
    baseName = os.path.splitext(os.path.basename(imagePath))[0]
    ra = co_args['ra']
    dec = co_args['dec']
    shape = cutout.shape
    return "{0}__{1}_{2}_{3}x{4}.fits".format(baseName, ra, dec, shape[0], shape[1])


# Parse, convert, and check the given arguments, returning a dictionary of cutout arguments.
# Any arguments needed by cutout routines should be passed through to the return dictionary.
def parse_cutout_args (args):
    co_args = parse_cutout_size(args)       # begin by getting cutout size parameters

    raStr = args.get("ra")
    if (not raStr):
        errMsg = "Right ascension must be specified, via the 'ra' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        ra = float(raStr)
        co_args['ra'] = ra

    decStr = args.get("dec")
    if (not decStr):
        errMsg = "Declination must be specified, via the 'dec' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        dec = float(decStr)
        co_args['dec'] = dec

    co_args['center'] = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame='icrs')

    filt = args.get("filter")
    if (not filt):
        errMsg = "An image filter must be specified, via the 'filter' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        co_args['filter'] = filt

    return co_args                          # return parsed, converted cutout arguments


# Parse, convert, and check the given cutout size arguments, return a dictionary of
# the size arguments. No returned cutout size signals that the whole image is desired.
def parse_cutout_size (args):
    co_args = {}                            # dictionary to hold parsed fields

    # read and parse a size specification in arc minutes or degrees
    sizeArcMinStr = args.get("sizeArcMin")
    sizeDegStr = args.get("sizeDeg")
    sizeArcSecStr = args.get("sizeArcSec")

    if (sizeArcMinStr):                     # prefer units in arc minutes
        co_args['units'] = u.arcmin
        co_args['size'] = float(sizeArcMinStr)
    elif (sizeDegStr):                      # alternatively in degrees
        co_args['units'] = u.deg
        co_args['size'] = float(sizeDegStr)
    elif (sizeArcSecStr):                   # or in arc seconds
        co_args['units'] = u.arcsec
        co_args['size'] = float(sizeArcSecStr)
    else:                                   # else no size specified
        co_args.pop('units', None)
        co_args['size'] = float(0)

    # make a scalar Quantity from the size and units, if possible
    if (co_args['size'] > 0):
        co_args['co_size'] = u.Quantity(co_args['size'], co_args['units'])
    else:
        co_args.pop('co_size', None)        # remove to signal that no sizes were given

    return co_args                          # return parsed, converted cutout arguments


# Send the specified image file, from the specified directory,
# back to the caller, giving it the specified MIME type.
def return_image (filename, imageDir=IMAGES_DIR, mimetype=FITS_MIME_TYPE):
    filepath = make_filepath_from_filename(filename, imageDir=imageDir)
    if (os.path.exists(filepath) and os.path.isfile(filepath)):
        return send_from_directory(imageDir, filename, mimetype=mimetype,
                                   as_attachment=True, attachment_filename=filename)
    errMsg = "Specified image file {0} not found in directory {1}".format(filename, imageDir)
    current_app.logger.error(errMsg)
    raise exceptions.ImageNotFound(errMsg)


# Write the contents of the given HDU to the specified file in the cutouts directory.
def write_cutout (hdu, co_filename, imageDir=CUTOUTS_DIR, overwrite=True):
    co_filepath = make_filepath_from_filename(co_filename, imageDir=imageDir)
    hdu.writeto(co_filepath, overwrite=True)


#
# Temporary methods
#

# return filename of an image from the specified image directory selected by the given cutout args
def find_image_filename (co_args, imageDir=IMAGES_DIR):
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
    else:
        return selected
