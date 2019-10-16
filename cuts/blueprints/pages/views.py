from flask import Blueprint, render_template, abort
# from jinja2 import TemplateNotFound

pages = Blueprint('pages', __name__, template_folder='templates')


@pages.route('/')
def index():
    return render_template('pages/index.html')


@pages.route('/about')
def about():
    return render_template('pages/about.html')


@pages.route('/license')
def license():
    return render_template('pages/license.html')


# default routing for pages
# @pages.route('/<page>')
# def show (page):
#     try:
#         return render_template('pages/%s.html' % page)
#     except TemplateNotFound:
#         abort(404)
