import os
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError
from cuts.blueprints.img.image_manager import ImageManager
from tests import TEST_DIR, TEST_DBCONFIG_FILEPATH

class TestImageManager(object):

    test_args = {
        'debug': True,
        'dbconfig_file': TEST_DBCONFIG_FILEPATH
    }

    imgr = ImageManager(test_args)


    def test_setup_app (self, app):
        " Create an instance of the app: should be executed only once by conftest.py. "
        assert app is not None


    def test_list_collections(self, client):
        lst = self.imgr.list_collections()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'DC19' in lst
        assert 'DC20' in lst
        assert 'JADES' in lst


    def test_list_filters(self, client):
        lst = self.imgr.list_filters()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'F090W' in lst
        assert 'F335M' in lst
        assert 'F444W' in lst


    def test_list_image_paths(self, client):
        lst = self.imgr.list_image_paths()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert '/vos/images/JADES/m13.fits' in lst
        assert '/vos/images/DC19/F090W.fits' in lst
        assert '/vos/images/DC20/F356W.fits' in lst
