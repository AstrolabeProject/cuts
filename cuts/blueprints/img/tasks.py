#
# Module to containing spawnable Celery tasks for the application.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Redo fetch and metadata methods. Add/use parse_id_arg method.
#
import os

from flask import current_app, jsonify, request, send_from_directory

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError, PartialOverlapError
from astropy.wcs import WCS

from config.settings import CUTOUTS_DIR, CUTOUTS_MODE, FITS_MIME_TYPE

import cuts.blueprints.img.file_utils as file_utils
from cuts.app import create_celery_app
from cuts.blueprints.img import exceptions
from cuts.blueprints.img.fits_utils import fits_file_exists
from cuts.blueprints.img.image_manager import ImageManager


# Instantiate the Celery client application
celery = create_celery_app()

# Instantiate the Image Manager
imgr = ImageManager()


#
# Image methods
#

@celery.task()
def fetch_image (args):
    """ Fetch a specific image by ID. """
    uid = parse_id_arg(args)                # get required ID or error
    return imgr.fetch_image(uid)


@celery.task()
def fetch_image_by_filter (args):
    """ Fetch a specific image by filter/collection. """
    filt = parse_filter_arg(args, required=True)  # get required filter or error
    collection = parse_collection_arg(args)
    return imgr.fetch_image_by_filter(filt, collection=collection)


@celery.task()
def fetch_image_by_path (args):
    """ Fetch a specific image by image path. """
    ipath = parse_ipath_arg(args, required=True)  # get required image path or error
    return imgr.fetch_image_by_path(ipath)


#############################################################

@celery.task()
def image_metadata (args):
    """ Return image metadata for a specific image by ID. """
    uid = parse_id_arg(args)                      # get required ID or error
    return jsonify(imgr.image_metadata(uid))


@celery.task()
def image_metadata_by_collection (args):
    """ Return image metadata for all images in a specific collection. """
    collection = parse_collection_arg(args, required=True)  # get required collection or error
    return jsonify(imgr.image_metadata_by_collection(collection))


@celery.task()
def image_metadata_by_filter (args):
    """ Return image metadata for all images with a specific filter/collection. """
    filt = parse_filter_arg(args, required=True)  # get required filter or error
    collection = parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.image_metadata_by_filter(filt, collection=collection))


@celery.task()
def image_metadata_by_path (args):
    """ Return image metadata for a specific image by image path. """
    ipath = parse_ipath_arg(args, required=True)  # get required image path or error
    return jsonify(imgr.image_metadata_by_path(ipath))


#############################################################

@celery.task()
def list_collections (args):
    """ List image collections found in the image metadata table. """
    return jsonify(imgr.list_collections())


@celery.task()
def list_filters (args):
    """ List image filters found in the image metadata table. """
    collection = parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.list_filters(collection=collection))


@celery.task()
def list_image_paths (args):
    """ List paths to FITS images from the image metadata table. """
    collection = parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.list_image_paths(collection=collection))


@celery.task()
def query_cone (args):
    """ List images which contain the given point within a given radius. """
    # parse the parameters for the location, radius, and collection
    co_args = parse_cutout_args(args)
    collection = parse_collection_arg(args)       # optional collection restriction
    filt = parse_filter_arg(args)                 # optional filter restriction
    return jsonify(imgr.query_cone(co_args, collection=collection, filt=filt))


@celery.task()
def query_image (args):
    """ List images which meet the given filter and collection criteria. """
    collection = parse_collection_arg(args)       # optional collection restriction
    filt = parse_filter_arg(args)                 # optional filter restriction
    return jsonify(imgr.query_image(collection=collection, filt=filt))



#
# Image cutout methods
#

@celery.task()
def list_cutouts (args):
    """ List all existing cutouts in the cutouts (cache) directory. """
    cutout_paths = [ fyl for fyl in file_utils.gen_file_paths(CUTOUTS_DIR) ]
    return jsonify(cutout_paths)


@celery.task()
def fetch_cutout_by_path (args):
    """ Fetch a specific image cutout by filepath. """
    filepath = args.get('path')
    if (not filepath):
        errMsg = "An image cutout file path must be specified, via the 'path' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    return return_cutout(filepath)


@celery.task()
def get_cutout (args):
    """ Make and return an image cutout. """

    # parse the parameters for the cutout
    co_args = parse_cutout_args(args)
    collection = parse_collection_arg(args)

    # figure out which image to make a cutout from based on the cutout parameters
    image_filepath = imgr.match_image(co_args, collection=collection)
    if (not image_filepath):
        errMsg = "No matching image was not found in images directory"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return imgr.return_image_at_filepath(image_filepath) # exit and return entire image

    # actually make the cutout
    hdu = fits.open(image_filepath)[0]
    cutout = make_cutout(hdu, co_args)

    # write the cutout to a new FITS file and then return it
    co_filename = make_cutout_filename(image_filepath, cutout, co_args, collection=collection)
    write_cutout(hdu, co_filename)

    return return_cutout(co_filename)       # return the image cutout


@celery.task()
def cutout_by_filter (args):
    """ Make and return an image cutout for a filtered image.
        The band is specified by the required 'filter' argument. """

    # parse the parameters for the cutout
    co_args = parse_cutout_args(args)
    collection = parse_collection_arg(args)
    filt = parse_filter_arg(args, required=True)  # test for required filter

    # figure out which image to make a cutout from based on the cutout parameters
    image_matches = imgr.query_cone(co_args, collection=collection, filt=filt)
    if (not image_matches):
        errMsg = f"An image was not found for filter {filt} in images directory"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        image_filepath = image_matches[0].get('file_path')

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return imgr.return_image_at_filepath(image_filepath) # exit and return entire image

    # actually make the cutout
    hdu = fits.open(image_filepath)[0]
    cutout = make_cutout(hdu, co_args)

    # write the cutout to a new FITS file and then return it
    co_filename = make_cutout_filename(image_filepath, cutout, co_args, collection=collection)
    write_cutout(hdu, co_filename)

    return return_cutout(co_filename)       # return the cutout image



#
# Internal helper methods
#

def make_cutout (hdu, co_args):
    """ Make and return an image cutout for the given image, based on the given cutout parameters. """
    wcs = WCS(hdu.header)

    # make the cutout and update its WCS info
    try:
        cutout = Cutout2D(hdu.data, position=co_args['center'], size=co_args['co_size'],
                          wcs=wcs, mode=CUTOUTS_MODE)
    except (NoOverlapError, PartialOverlapError):
        sky = co_args['center']
        errMsg = f"There is no overlap between the reference image and the given center coordinate: {sky.ra.value}, {sky.dec.value} {sky.ra.unit.name} ({sky.frame.name})"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)

    # save cutout image in the FITS HDU and update FITS header with cutout WCS
    hdu.data = cutout.data
    hdu.header.update(cutout.wcs.to_header())

    return cutout


def make_cutout_filename (image_filepath, cutout, co_args, collection=None):
    """ Return a filename for the Astropy cutout from info in the given parameters. """
    basename = os.path.splitext(os.path.basename(image_filepath))[0]
    ra = co_args['ra']
    dec = co_args['dec']
    shape = cutout.shape
    coll = collection if (collection is not None) else '_'
    return f"{coll}_{basename}__{ra}_{dec}_{shape[0]}x{shape[1]}.fits"


def parse_collection_arg (args, required=False):
    """
    Parse out the collection argument, returning the collection name string or None,
    if no collection argument given.
    :raises: RequestException if no collection given and the required flag is True.
    """
    collection = args.get('collection', args.get('coll'))
    if (collection is not None):
        collection = collection.strip()
        if ((not collection) and required):
            errMsg = "A collection name must be specified, via the 'collection' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
    return collection


def parse_coordinate_args (args):
    """ Parse, convert, and check the given coordinate arguments, returning a dictionary
        of coordinate arguments. """
    co_args = {}

    raStr = args.get('ra')
    if (not raStr):
        errMsg = "Right ascension must be specified, via the 'ra' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        ra = float(raStr)
        co_args['ra'] = ra

    decStr = args.get('dec')
    if (not decStr):
        errMsg = "Declination must be specified, via the 'dec' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        dec = float(decStr)
        co_args['dec'] = dec

    frame = args.get('frame', 'icrs')       # get optional coordinate reference system

    co_args['center'] = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame=frame)

    return co_args                          # return parsed, converted cutout arguments


def parse_cutout_args (args):
    """ Parse, convert, and check the given arguments, returning a dictionary
        of cutout arguments. Any arguments needed by cutout routines should be passed
        through to the return dictionary.
    """
    co_args = parse_cutout_size(args)            # begin by getting cutout size parameters
    co_args.update(parse_coordinate_args(args))  # add coordinate parameters
    return co_args                               # return parsed, converted cutout arguments


def parse_cutout_size (args):
    """ Parse, convert, and check the given cutout size arguments, return a dictionary of
        the size arguments. No returned cutout size signals that the whole image is desired. """
    co_args = {}                            # dictionary to hold parsed fields

    # read and parse a size specification in arc minutes or degrees
    sizeArcMinStr = args.get('sizeArcMin')
    sizeDegStr = args.get('sizeDeg', args.get('radius'))  # allow alternate radius keyword
    sizeArcSecStr = args.get('sizeArcSec')

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


def parse_ipath_arg (args, required=False):
    """
    Parse out the file path argument, returning the file path string or None.
    :raises: RequestException if no path given and the required flag is True.
    """
    filepath = args.get('path')
    if (filepath is not None):
        filepath = filepath.strip()
        if ((not filepath) and required):
            errMsg = "An image file path must be specified, via the 'path' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
    return filepath


def parse_filter_arg (args, required=False):
    """
    Parse out the filter argument, returning the filter name string or None.
    :raises: RequestException if no filter given and the required flag is True.
    """
    filt = args.get('filter')
    if (filt is not None):
        filt = filt.strip()
        if ((not filt) and required):
            errMsg = "An image filter must be specified, via the 'filter' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
    return filt


def parse_id_arg (args, required=True):
    """
    Parse out the unique ID argument, returning the ID or None, if no ID
    argument is given or if the ID is not covertible to a positive integer > 0.
    :raises: RequestException if no ID given and the required flag is True.
    """
    uid = args.get('id')
    if (uid is not None):
        uid = uid.strip()
        try:
            num = int(uid)
            if (num > 0):
                return num
        except ValueError:
            pass                            # drop through to error

    if (not required):
        return None
    else:
        errMsg = "A record ID must be specified, via the 'id' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)


def return_cutout (co_filename, mimetype=FITS_MIME_TYPE):
    """ Return the named cutout file, giving it the specified MIME type. """
    co_filepath = os.path.join(CUTOUTS_DIR, co_filename)
    if (fits_file_exists(co_filepath)):
        return send_from_directory(CUTOUTS_DIR, co_filename, mimetype=mimetype,
                                   as_attachment=True, attachment_filename=co_filename)
    errMsg = f"Specified image cutout file '{co_filename}' not found in cutouts directory"
    current_app.logger.error(errMsg)
    raise exceptions.ImageNotFound(errMsg)


def write_cutout (hdu, co_filename, overwrite=True):
    """ Write the contents of the given HDU to the named file in the cutouts directory. """
    co_filepath = os.path.join(CUTOUTS_DIR, co_filename)
    hdu.writeto(co_filepath, overwrite=True)
