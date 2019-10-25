from flask import Blueprint, abort, jsonify, request
# from flask_cors import CORS

img = Blueprint('img', __name__, template_folder='templates')


#
# Full image methods
#

# list all FITS images found in the image directory
@img.route('/img/list')
def list ():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_images
    return list_images()

@img.route('/img/<name>', methods=['GET'])
def fetch (name):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import fetch_image
    return fetch_image(name)


#
# Image cutout methods
#

# Use Astrocut to produce and return a cutout
@img.route('/img/ac')
def cutout_ac (args):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import get_astrocut_cutout
    return get_astrocut_cutout(request.args)


@img.route('/echo')
def echo ():
    return jsonify(request.args)
