#
# Module containing spawnable Celery tasks for the application.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Refactor argument handling/parsing into separate module.
#
import os

from flask import current_app, jsonify, request

import cuts.blueprints.img.arg_utils as au
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
    uid = au.parse_id_arg(args)                   # get required ID or error
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
    filt = au.parse_filter_arg(args, required=True)  # get required filter or error
    collection = au.parse_collection_arg(args)
    istream = imgr.fetch_image_by_filter(filt, collection=collection)
    if (istream is not None):
        return istream
    else:
        coll = f"and collection '{collection}'" if (collection) else ''
        errMsg = f"Image with filter '{filt}' {coll} not found in database"
        current_app.logger.error(errMsg)
        raise exceptions.ImageNotFound(errMsg)


@celery.task()
def fetch_image_by_path (args):
    """ Fetch a specific image by image path. """
    ipath = au.parse_ipath_arg(args, required=True)  # get required image path or error
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
    uid = au.parse_id_arg(args)                   # get required ID or error
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
    collection = au.parse_collection_arg(args, required=True)  # get required collection or error
    return jsonify(imgr.image_metadata_by_collection(collection))


@celery.task()
def image_metadata_by_filter (args):
    """ Return image metadata for all images with a specific filter/collection. """
    filt = au.parse_filter_arg(args, required=True)  # get required filter or error
    collection = au.parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.image_metadata_by_filter(filt, collection=collection))


@celery.task()
def image_metadata_by_path (args):
    """ Return image metadata for a specific image by image path. """
    ipath = au.parse_ipath_arg(args, required=True)  # get required image path or error
    collection = au.parse_collection_arg(args)       # optional collection restriction
    return jsonify(imgr.image_metadata_by_path(ipath, collection=collection))


#############################################################

@celery.task()
def list_collections (args):
    """ List image collections found in the image metadata table. """
    return jsonify(imgr.list_collections())


@celery.task()
def list_filters (args):
    """ List image filters found in the image metadata table. """
    collection = au.parse_collection_arg(args)    # optional collection restriction
    return jsonify(imgr.list_filters(collection=collection))


@celery.task()
def list_image_paths (args):
    """ List paths to FITS images from the image metadata table. """
    collection = au.parse_collection_arg(args)    # optional collection restriction
    return jsonify(imgr.list_image_paths(collection=collection))


@celery.task()
def query_cone (args):
    """
    Return some metadata for images which contain the given point within a given radius.
    """
    co_args = au.parse_cutout_args(args, required=True)  # get coordinates and radius
    collection = au.parse_collection_arg(args)           # optional collection restriction
    filt = au.parse_filter_arg(args)                     # optional filter restriction
    return jsonify(imgr.query_cone(co_args, collection=collection, filt=filt))


@celery.task()
def query_image (args):
    """ List images which meet the given filter and collection criteria. """
    collection = au.parse_collection_arg(args)    # optional collection restriction
    filt = au.parse_filter_arg(args)              # optional filter restriction
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
    co_args = au.parse_cutout_args(args)    
    collection = au.parse_collection_arg(args)

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
    co_args = au.parse_cutout_args(args)
    collection = au.parse_collection_arg(args)
    filt = au.parse_filter_arg(args, required=True)  # test for required filter

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
