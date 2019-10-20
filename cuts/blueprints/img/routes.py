from flask import Blueprint, abort, render_template, request
# from flask_cors import CORS
from jinja2 import TemplateNotFound


img = Blueprint('img', __name__, template_folder='templates')


@img.route('/img/list')
def list():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import list_images
    return list_images()


@img.route('/img/query')
def query():
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import query_images
    return query_images(request.args)


@img.route('/img/<name>', methods=['GET'])
def image(name):
    # required to avoid circular imports
    from cuts.blueprints.img.tasks import send_image
    return send_image(name)


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
