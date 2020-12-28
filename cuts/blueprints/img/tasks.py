#
# Module containing spawnable Celery tasks for the application.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Redo parse_filter_arg.
#
import os

from flask import current_app, jsonify, request

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord

from cuts.app import create_celery_app
from cuts.blueprints.img import exceptions
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
    uid = parse_id_arg(args)                      # get required ID or error
    istream = imgr.fetch_image(uid)
    if (istream is not None):
        return istream
    else:
        errMsg = f"Image with image ID '{uid}' not found in database"
        current_app.logger.error(errMsg)
        raise exceptions.ImageNotFound(errMsg)


@celery.task()
def fetch_image_by_filter (args):
    """ Fetch a specific image by filter/collection. """
    filt = parse_filter_arg(args, required=True)  # get required filter or error
    collection = parse_collection_arg(args)
    istream = imgr.fetch_image_by_filter(filt, collection=collection)
    if (istream is not None):
        return istream
    else:
        coll = f" and collection '{collection}' " if (collection) else ''
        errMsg = f"Image with filter '{filt}' {coll} not found in database"
        current_app.logger.error(errMsg)
        raise exceptions.ImageNotFound(errMsg)


@celery.task()
def fetch_image_by_path (args):
    """ Fetch a specific image by image path. """
    ipath = parse_ipath_arg(args, required=True)  # get required image path or error
    istream = imgr.fetch_image_by_path(ipath)
    if (istream is not None):
        return istream
    else:
        errMsg = f"Image with image path '{ipath}' not found in database"
        current_app.logger.error(errMsg)
        raise exceptions.ImageNotFound(errMsg)


#############################################################

@celery.task()
def image_metadata (args):
    """ Return image metadata for a specific image by ID. """
    uid = parse_id_arg(args)                      # get required ID or error
    md = imgr.image_metadata(uid)
    if (md is not None):
        return jsonify(imgr.image_metadata(uid))
    else:
        errMsg = f"Image metadata for image ID '{uid}' not found in database"
        current_app.logger.error(errMsg)
        raise exceptions.ImageNotFound(errMsg)


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
    collection = parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.image_metadata_by_path(ipath, collection=collection))


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
    """
    Return some metadata for images which contain the given point within a given radius.
    """
    co_args = parse_cutout_args(args, required=True)  # get coordinates and radius
    collection = parse_collection_arg(args)           # optional collection restriction
    filt = parse_filter_arg(args)                     # optional filter restriction
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
    return jsonify(imgr.list_cutouts())


@celery.task()
def get_cutout (args):
    """
    Return an image cutout. if cutout size is not specified, return the entire image.
    """
    # parse the parameters for the cutout
    co_args = parse_cutout_args(args)    
    collection = parse_collection_arg(args)

    # figure out which image to make a cutout from based on the cutout parameters
    image_matches = imgr.query_cone(co_args, collection=collection)   
    if (not image_matches):
        errMsg = "No matching image was not found."
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        image_path = image_matches[0].get('file_path')

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return imgr.return_image_at_path(image_path)  # exit and return entire image
    else:                                   # else make, cache, and return cutout
        return imgr.get_cutout(image_path, co_args, collection=collection)


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
        errMsg = f"No matching image was not found for filter '{filt}'."
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        image_path = image_matches[0].get('file_path')

    if (not co_args.get('co_size')):        # if no size specified, return the entire image
        return imgr.return_image_at_path(image_path)  # exit and return entire image
    else:                                   # else make, cache, and return cutout
        return imgr.get_cutout(image_path, co_args, collection=collection)


@celery.task()
def fetch_cutout_by_filename (args):
    """ Fetch a specific image cutout by filename. """
    filename = args.get('filename')
    if (not filename):
        errMsg = "An image cutout filename must be specified, via the 'filename' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    return imgr.return_cutout_with_name(filename)



#
# Internal helper methods
#

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


def parse_cutout_args (args, required=False):
    """ Parse, convert, and check the given arguments, returning a dictionary
        of cutout arguments. Any arguments needed by cutout routines will be passed
        through to the return dictionary.
    """
    co_args = parse_cutout_size(args, required=required)  # first, get cutout size parameters
    co_args.update(parse_coordinate_args(args))  # add coordinate parameters
    return co_args                               # return parsed, converted cutout arguments


def parse_cutout_size (args, required=False):
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

    if (co_args.get('size') is None):       # if no size given
        if (required):                      # if size argument required
            errMsg = "A radius size (one of 'radius', 'sizeDeg', 'sizeArcMin', or 'sizeArcSec') must be specified."
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        return co_args                      # not required: return empty dictionary

    # got a size: make a scalar Quantity from the size and units, if possible
    co_args['co_size'] = u.Quantity(co_args['size'], co_args['units'])
    return co_args                          # return parsed, converted cutout arguments


def parse_id_arg (args, required=True):
    """
    Parse out the unique ID argument, returning the ID or None, if no ID
    argument is given or if the ID is not covertible to a positive integer > 0.
    :raises: RequestException if no ID given and the required flag is True.
    """
    uid = args.get('id')
    if (uid is not None):
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


def parse_ipath_arg (args, required=False):
    """
    Parse out the file path argument, returning the file path string or None.
    :raises: RequestException if no path given and the required flag is True.
    """
    filepath = args.get('path')
    if (filepath is not None):
        filepath = filepath.strip()
        if ((not filepath) and required):
            errMsg = "A valid image path must be specified, via the 'path' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
    return filepath


def parse_filter_arg (args, required=False):
    """
    Parse out the filter argument, returning the filter name string or None.
    :raises: RequestException if no filter given and the required flag is True.
    """
    filt = args.get('filter')
    if ((filt is None) or (not filt.strip())):    # if no filter or empty filter
        if (required):
            errMsg = "An image filter must be specified, via the 'filter' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        else:
            return None
    return filt.strip()
