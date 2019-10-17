import glob, os

from flask import Blueprint, abort, jsonify, render_template, send_file
# from flask_cors import CORS
from jinja2 import TemplateNotFound
from config.settings import IMAGES_DIR, IMAGE_EXTS


img = Blueprint('img', __name__, template_folder='templates')


@img.route('/img/list')
def list():
    fyls = [ fyl for fyl in os.listdir(IMAGES_DIR) if (fyl.endswith(tuple(IMAGE_EXTS))) ]
    return jsonify(fyls)
    # return jsonify(glob.glob("*.fits"))


@img.route('/img/<name>', methods=['GET'])
def image(name):
    filename = "{0}/{1}".format(IMAGES_DIR, name)
    if (os.path.exists(filename) and os.path.isfile(filename)):
        return send_file(filename, mimetype='application/fits')
    abort(404)


@img.route('/img/help')
def help():
    return render_template('help/help.html')

# general routing for image help pages
@img.route('/img/help/<topic>')
def show_help (topic):
    try:
        return render_template('help/%s.html' % topic)
    except TemplateNotFound:
        abort(404)
