#
# Top-level Flask routing module: answers requests or spawns Celery task to do it.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Change URLs for all cutout methods. Rename some cutout methods.
#
from flask import Blueprint, jsonify, request
# from flask_cors import CORS
from cuts.blueprints.img import exceptions


# Instantiate the image blueprint
img = Blueprint('img', __name__, template_folder='templates')


#
# Image methods
#
@img.route('/img/fetch_by_filepath')
def img_fetch_by_filepath ():
    """ Fetch a specific image by filepath. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image_by_filepath
    return fetch_image_by_filepath(request.args)


@img.route('/img/fetch_by_filter')
def img_fetch_by_filter ():
    """ Fetch a specific image by image filter/collection. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image_by_filter
    return fetch_image_by_filter(request.args)


@img.route('/img/metadata_by_filepath')
def img_metadata_by_filepath ():
    """ Fetch image metadata for a specific image by filepath/collection. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import image_metadata_by_filepath
    return image_metadata_by_filepath(request.args)


@img.route('/img/metadata_by_filter')
def img_metadata_by_filter ():
    """ Fetch image metadata for a specific image by filter/collection. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import image_metadata_by_filter
    return image_metadata_by_filter(request.args)


@img.route('/img/list_collections')
def list_collections ():
    """ List image collections found in the image metadata table. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_collections
    return list_collections(request.args)


@img.route('/img/list_image_paths')
def list_image_paths ():
    """ List paths to FITS images from the image metadata table. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_image_paths
    return list_image_paths(request.args)


@img.route('/img/list_filters')
def list_filters ():
    """ List image filters found in the image metadata table. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_filters
    return list_filters(request.args)


@img.route('/img/query_cone')
def query_cone ():
    """ List images which contain the given point within a given radius. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import query_cone
    return query_cone(request.args)


@img.route('/img/query_image')
def query_image ():
    """ List images which meet the given filter and collection criteria. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import query_image
    return query_image(request.args)



#
# Image cutout methods
#

@img.route('/co/list')
def co_list ():
    """ List all existing cutouts in the cutouts (cache) directory. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_cutouts
    return list_cutouts(request.args)


@img.route('/co/fetch_by_filepath')
def co_fetch_by_filepath ():
    """ Fetch a specific cutout by filepath. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_cutout_by_filepath
    return fetch_cutout_by_filepath(request.args)


@img.route('/co/cutout')
def co_cutout ():
    """ Make and return an image cutout. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_cutout
    return get_cutout(request.args)


@img.route('/co/cutout_by_filter')
def co_cutout_by_filter ():
    """ Make and return an image cutout for an image in a certain bandwidth. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import cutout_by_filter
    return cutout_by_filter(request.args)


@img.route('/echo')
def echo ():
    """ Echo the Request arguments as a JSON data structure. """
    return jsonify(request.args)


#
# Image blueprint error handlers
#

@img.errorhandler(exceptions.RequestException)
def handle_request_exception(exception):
    return exception.to_tuple()

@img.errorhandler(exceptions.ImageNotFound)
def handle_image_not_found(exception):
    return exception.to_tuple()

@img.errorhandler(exceptions.ServerException)
def handle_server_exception(exception):
    return exception.to_tuple()
