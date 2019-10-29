from flask import Blueprint, abort, jsonify, request
# from flask_cors import CORS
from config.settings import CUTOUTS_LIB

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

# fetch a specific image by full name
@img.route('/img/<name>', methods=['GET'])
def img_fetch (name):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image
    return fetch_image(name)


#
# Image cutout methods
#

# list all existing cutouts in the cache directory
@img.route('/img/co/list')
def co_list ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_cutouts
    return list_cutouts()

# fetch a specific cutout by full name
@img.route('/img/co/<name>', methods=['GET'])
def co_fetch (name):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_cutout
    return fetch_cutout(name)


# Use configuration to decide which cutout library to use
@img.route('/img/co/cut')
def co_cut ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astrocut_cutout
    from cuts.blueprints.img.tasks import get_astropy_cutout
    if (CUTOUTS_LIB and CUTOUTS_LIB == 'astrocut'):
        return get_astrocut_cutout(request.args)
    else:
        return get_astropy_cutout(request.args)

# Use Astropy Cutout2D to produce and return a cutout
@img.route('/img/co/2d')
def co_2d ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astropy_cutout
    return get_astropy_cutout(request.args)

# Use Astrocut to produce and return a cutout
@img.route('/img/co/ac')
def co_ac ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astrocut_cutout
    return get_astrocut_cutout(request.args)


@img.route('/echo')
def echo ():
    return jsonify(request.args)
