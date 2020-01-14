#
# Module to containing spawnable Celery tasks for the application.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Update for rename to list_fits_paths.
#
import os

from flask import current_app, jsonify, request, send_file, send_from_directory

from cuts.app import create_celery_app
from config.settings import CUTOUTS_DIR, CUTOUTS_MODE, FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS
from cuts.blueprints.img import exceptions
import cuts.blueprints.img.image_manager as imgr

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

# List all FITS images found in the image directory.
@celery.task()
def list_images (args):
    collection = args.get("collection")
    image_files = imgr.list_fits_paths(collection=collection)
    return jsonify(image_files)


# Fetch a specific image by filename.
@celery.task()
def fetch_image (filename):
    return return_image(filename)


# Tell whether the specified image contains the specified coordinate or not.
@celery.task()
def image_contains (filename, args):
    coords = parse_coordinate_args(args)
    res = imgr.image_contains(filename, coords)
    return jsonify([imgr.image_contains(filename, coords)])


# Return the corner coordinates of the specified image.
@celery.task()
def image_corners (filename):
    return jsonify(imgr.image_corners(filename))


#
# Image cutout methods
#

# List all existing cutouts in the cache directory.
@celery.task()
def list_cutouts ():
    image_files = imgr.list_fits_paths(imageDir=CUTOUTS_DIR)
    return jsonify(image_files)


# Fetch a specific cutout by filename.
@celery.task()
def fetch_cutout (filename):
    return return_image(filename, imageDir=CUTOUTS_DIR)


# Make and return an image cutout.
@celery.task()
def get_cutout (args):
    # parse the parameters for the cutout
    co_args = parse_cutout_args(args)

    # figure out which image to make a cutout from based on the cutout parameters
    image_filename = imgr.match_image(co_args)
    if (not image_filename):
        errMsg = "No matching image was not found in images directory {0}".format(IMAGES_DIR)
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return return_image(image_filename) # exit out now, returning entire image

    # compute the image filepath and actually make the cutout
    image_path = imgr.image_filepath_from_filename(image_filename)
    hdu = fits.open(image_path)[0]
    cutout = make_cutout(hdu, co_args)

    # write the cutout to a new FITS file and then return it
    co_filename = make_cutout_filename(image_filename, cutout, co_args)
    write_cutout(hdu, co_filename)

    return return_image(co_filename, imageDir=CUTOUTS_DIR) # return the cutout image


# Make and return an image cutout for a filtered image.
# The band is specified by the non-optional 'filter' argument.
@celery.task()
def get_cutout_by_filter (args):
    # parse the parameters for the cutout
    co_args = parse_cutout_args(args, filterRequired=True)

    # figure out which image to make a cutout from based on the cutout parameters
    filt = co_args.get('filter')
    image_filename = imgr.match_image(co_args, match_fn=imgr.by_filter_matcher)
    if (not image_filename):
        errMsg = "An image was not found for filter {0} in images directory {1}".format(filt, IMAGES_DIR)
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return return_image(image_filename) # exit out now, returning entire image

    # compute the image filepath and actually make the cutout
    image_path = imgr.image_filepath_from_filename(image_filename)
    hdu = fits.open(image_path)[0]
    cutout = make_cutout(hdu, co_args)

    # write the cutout to a new FITS file and then return it
    co_filename = make_cutout_filename(image_filename, cutout, co_args)
    write_cutout(hdu, co_filename)

    return return_image(co_filename, imageDir=CUTOUTS_DIR) # return the cutout image


@celery.task()
def show_cache (args):
    return imgr.show_cache()


#
# Internal helper methods
#

# Make and return an image cutout for the given image, based on the given cutout parameters.
def make_cutout (hdu, co_args):
    wcs = WCS(hdu.header)

    # make the cutout and update its WCS info
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

    return cutout


# Return a filename for the Astropy cutout from info in the given parameters
def make_cutout_filename (image_path, cutout, co_args):
    baseName = os.path.splitext(os.path.basename(image_path))[0]
    ra = co_args['ra']
    dec = co_args['dec']
    shape = cutout.shape
    return "{0}__{1}_{2}_{3}x{4}.fits".format(baseName, ra, dec, shape[0], shape[1])


# Parse, convert, and check the given coordinate arguments, returning a dictionary of
# coordinate arguments.
def parse_coordinate_args (args):
    co_args = {}

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

    return co_args                          # return parsed, converted cutout arguments


# Parse, convert, and check the given arguments, returning a dictionary of cutout arguments.
# Any arguments needed by cutout routines should be passed through to the return dictionary.
def parse_cutout_args (args, filterRequired=False):
    co_args = parse_cutout_size(args)       # begin by getting cutout size parameters

    co_args.update(parse_coordinate_args(args)) # add coordinate parameters

    filt = args.get("filter")
    if (filt):
        co_args['filter'] = filt
    else:
        if (filterRequired):
            errMsg = "An image filter must be specified, via the 'filter' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)

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
    if (imgr.fits_file_exists(filename, imageDir)):
        return send_from_directory(imageDir, filename, mimetype=mimetype,
                                   as_attachment=True, attachment_filename=filename)
    errMsg = "Specified image file {0} not found in directory {1}".format(filename, imageDir)
    current_app.logger.error(errMsg)
    raise exceptions.ImageNotFound(errMsg)


# Write the contents of the given HDU to the specified file in the cutouts directory.
def write_cutout (hdu, co_filename, imageDir=CUTOUTS_DIR, overwrite=True):
    co_filepath = imgr.image_filepath_from_filename(co_filename, imageDir=imageDir)
    hdu.writeto(co_filepath, overwrite=True)
