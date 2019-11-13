from flask import Blueprint, jsonify, request
# from flask_cors import CORS
from config.settings import CUTOUTS_LIB
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

# fetch a specific image by filename
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


# Use Astropy Cutout2D to produce and return a cutout
@img.route('/img/co/2d')
def co_2d ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astropy_cutout
    return get_astropy_cutout(request.args)

# Make and return cutout using Astropy Cutout2D
@img.route('/img/co/cut')
def co_cut ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astropy_cutout
    return get_astropy_cutout(request.args)


# # Use configuration to decide which cutout library to use
# @img.route('/img/co/cut')
# def co_cut ():
#     # required to avoid circular imports
#     from cuts.blueprints.img.tasks import get_astrocut_cutout
#     from cuts.blueprints.img.tasks import get_astropy_cutout
#     if (CUTOUTS_LIB and CUTOUTS_LIB == 'astrocut'):
#         return get_astrocut_cutout(request.args)
#     else:
#         return get_astropy_cutout(request.args)

# # Use Astrocut to produce and return a cutout
# @img.route('/img/co/ac')
# def co_ac ():
#     # required to avoid circular imports
#     from cuts.blueprints.img.tasks import get_astrocut_cutout
#     return get_astrocut_cutout(request.args)


@img.route('/echo')
def echo ():
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
