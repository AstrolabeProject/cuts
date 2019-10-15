from flask import Blueprint, render_template

pages = Blueprint('pages', __name__, template_folder='templates')


@pages.route('/')
def home():
    return render_template('pages/home.html')


@pages.route('/about')
def about():
    return render_template('pages/about.html')


@pages.route('/license')
def license():
    return render_template('pages/license.html')
