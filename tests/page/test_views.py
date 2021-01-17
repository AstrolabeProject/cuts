from flask import url_for


class TestPage(object):
    def test_home_page(self, client):
        """ Home page should respond with a success 200. """
        response = client.get(url_for('pages.index'))
        assert response.status_code == 200


    def test_license_page(self, client):
        """ License Terms page should respond with a success 200. """
        response = client.get(url_for('pages.license'))
        assert response.status_code == 200


    def test_about_page(self, client):
        """ About page should respond with a success 200. """
        response = client.get(url_for('pages.about'))
        assert response.status_code == 200


    def test_help_page(self, client):
        """ Help page should respond with a success 200. """
        response = client.get('/help')
        assert response.status_code == 200


    def test_show_help(self, client):
        """ Help <bad topic> page should respond with an error 404. """
        response = client.get('/help/NONE')
        assert response.status_code == 404
