#
# Top-level Flask routing module: answers requests or spawns Celery task to do it.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Update for list image paths method.
#
from flask import Blueprint, jsonify, request
# from flask_cors import CORS
from cuts.blueprints.img import exceptions


# Instantiate the image blueprint
img = Blueprint('img', __name__, template_folder='templates')


#
# Full image methods
#

@img.route('/img/list')
def img_paths_list ():
    """ List FITS images found in the image directory or a sub-collection. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_image_paths
    return list_image_paths(request.args)


@img.route('/img/fetch')
def img_fetch ():
    """ Fetch a specific image by filepath. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image
    return fetch_image(request.args)


@img.route('/img/collections/list')
def coll_list ():
    """ List image collections found in the image directory. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_collections
    return list_collections(request.args)


#
# Image cutout methods
#

@img.route('/img/co/list')
def co_list ():
    """ List all existing cutouts in the cache directory. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_cutouts
    return list_cutouts(request.args)


@img.route('/img/co/fetch')
def co_fetch ():
    """ Fetch a specific cutout by filepath. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_cutout
    return fetch_cutout(request.args)


@img.route('/img/co/cutout')
def co_cutout ():
    """ Make and return an image cutout. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_cutout
    return get_cutout(request.args)


@img.route('/img/co/cutout_by_filter')
def co_cutout_by_filter ():
    """ Make and return an image cutout for an image in a certain bandwidth. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_cutout_by_filter
    return get_cutout_by_filter(request.args)


@img.route('/echo')
def echo ():
    """ Echo the Request arguments as a JSON data structure. """
    return jsonify(request.args)


@img.route('/admin/show_cache')
def admin_show_cache ():
    """ Show the current contents of the image cache. """
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import show_cache
    return show_cache(request.args)


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
