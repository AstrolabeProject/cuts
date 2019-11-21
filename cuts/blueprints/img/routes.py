from flask import Blueprint, jsonify, request
# from flask_cors import CORS
from cuts.blueprints.img import exceptions


# Instantiate the image blueprint
img = Blueprint('img', __name__, template_folder='templates')


#
# Full image methods
#

# list all FITS images found in the image directory
@img.route('/img/list')
def img_list ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_images
    return list_images()

# fetch a specific image by filename
@img.route('/img/<filename>', methods=['GET'])
def img_fetch (filename):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image
    return fetch_image(filename)

# tell whether the specified image contains the specified coordinate
@img.route('/img/contains/<filename>', methods=['GET'])
def img_contains (filename):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import image_contains
    return image_contains(filename, request.args)

# return the corner coordinates of the specified image
@img.route('/img/corners/<filename>', methods=['GET'])
def img_corners (filename):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import image_corners
    return image_corners(filename)


#
# Image cutout methods
#

# list all existing cutouts in the cache directory
@img.route('/img/co/list')
def co_list ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_cutouts
    return list_cutouts()

# fetch a specific cutout by filename
@img.route('/img/co/<filename>', methods=['GET'])
def co_fetch (filename):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_cutout
    return fetch_cutout(filename)


# Make and return an image cutout
@img.route('/img/co/cutout')
def co_cutout ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_cutout
    return get_cutout(request.args)

# Make and return an image cutout for an image in a certain bandwidth
@img.route('/img/co/cutout_by_filter')
def co_cutout_by_filter ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_cutout_by_filter
    return get_cutout_by_filter(request.args)


@img.route('/echo')
def echo ():
    return jsonify(request.args)

@img.route('/admin/show_cache')
def admin_show_cache ():
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
