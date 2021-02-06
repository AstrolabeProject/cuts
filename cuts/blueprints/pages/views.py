from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

pages = Blueprint('pages', __name__, template_folder='templates')


# General pages
#
@pages.route('/')
def index():
    return render_template('pages/index.html')


@pages.route('/about')
def about():
    return render_template('pages/about.html')


@pages.route('/api')
def api():
    return render_template('pages/api.html')


@pages.route('/license')
def license():
    return render_template('pages/license.html')


# Help methods
#

# general routing for help pages
@pages.route('/help/<topic>')
def show_help (topic):
    try:
        return render_template('help/%s.html' % topic)
    except TemplateNotFound:
        abort(404)

# main help page
@pages.route('/help')
def help():
    return render_template('help/help.html')


# default routing for pages
# @pages.route('/<page>')
# def show (page):
#     try:
#         return render_template('pages/%s.html' % page)
#     except TemplateNotFound:
#         abort(404)
