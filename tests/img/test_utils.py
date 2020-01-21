import cuts.blueprints.img.utils as utils

import os
# import sys
import pytest

class TestUtils(object):

    def test_is_fits_file(self):
        assert utils.is_fits_file('m13.fits') == True
        assert utils.is_fits_file('m13.fits.gz') == True
        assert utils.is_fits_file('/usr/dummy/m13.fits') == True
        assert utils.is_fits_file('/usr/dummy/m13.fits.gz') == True

        assert utils.is_fits_file('m13') == False
        assert utils.is_fits_file('m13-fits') == False
        assert utils.is_fits_file('m13.gz') == False
        assert utils.is_fits_file('/usr/dummy/m13') == False
        assert utils.is_fits_file('/usr/dummy/m13-fits') == False
        assert utils.is_fits_file('/usr/dummy/m13.gz') == False


    def test_is_fits_filename(self):
        assert utils.is_fits_filename('m13.fits') == True
        assert utils.is_fits_filename('m13.fits.gz') == True
        assert utils.is_fits_filename('/usr/dummy/m13.fits') == True
        assert utils.is_fits_filename('/usr/dummy/m13.fits.gz') == True

        assert utils.is_fits_filename('m13') == False
        assert utils.is_fits_filename('m13.gz') == False
        assert utils.is_fits_filename('m13-fits') == False
        assert utils.is_fits_filename('/usr/dummy/m13') == False
        assert utils.is_fits_filename('/usr/dummy/m13-fits') == False
        assert utils.is_fits_filename('/usr/dummy/m13.gz') == False


    def test_gen_file_paths(self):
        paths = [ p for p in utils.gen_file_paths(os.getcwd()) ]
        assert len(paths) != 0, "The generated path list for PWD is not empty."

        paths = [ p for p in utils.gen_file_paths('/tmp/HiGhLyUnLiKeLy') ]
        assert len(paths) == 0, "The generated path list for non-existant directory is empty."


    def test_metadata_keys(self):
        assert utils.get_metadata_keys({}) == None
        assert utils.get_metadata_keys({'keymissing': True}) == None
        assert utils.get_metadata_keys({'keyfile': None}) == None

        mdkeys = utils.get_metadata_keys({'keyfile': '/cuts/tests/resources/empty.txt'})
        assert len(mdkeys) == 0

        mdkeys = utils.get_metadata_keys({'keyfile': '/cuts/tests/resources/mdkeys.txt'})
        assert len(mdkeys) == 13

        with pytest.raises(FileNotFoundError):
            utils.get_metadata_keys({'keyfile': 'bad_filename'})


    def test_path_has_dots(self):
        assert utils.path_has_dots('.') == True
        assert utils.path_has_dots('..') == True
        assert utils.path_has_dots('./..') == True
        assert utils.path_has_dots('./usr/dummy/') == True
        assert utils.path_has_dots('../usr/dummy/') == True
        assert utils.path_has_dots('/usr/dummy/./smarty') == True
        assert utils.path_has_dots('/usr/dummy/../smarty') == True
        assert utils.path_has_dots('/usr/dummy/.') == True
        assert utils.path_has_dots('/usr/dummy/..') == True

        assert utils.path_has_dots('dummy') == False
        assert utils.path_has_dots('dummy.txt') == False
        assert utils.path_has_dots('dummy.file.txt') == False
        assert utils.path_has_dots('/') == False
        assert utils.path_has_dots('/dummy') == False
        assert utils.path_has_dots('/usr/dummy') == False
        assert utils.path_has_dots('/usr/dummy/') == False
