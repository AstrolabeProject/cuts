# Tests for the image manager module.
#   Written by: Tom Hicks. 1/9/2021.
#   Last Modified: Update for collection cleaning, extras to XTRAS.
#
import os
import pytest

from astropy import units as u

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError
from cuts.blueprints.img.image_manager import IRODS_ZONE_NAME, ImageManager
from tests import TEST_RESOURCES_DIR, TEST_DBCONFIG_FILEPATH

class TestImageManager(object):

    test_args = {
        'debug': True,
        'dbconfig_file': TEST_DBCONFIG_FILEPATH
    }

    bad_path = '/bad/path'
    m13_path = '/vos/images/XTRAS/m13.fits'
    dc19_path = '/vos/images/DC19/F090W.fits'
    dc20_path = '/vos/images/DC20/F356W.fits'
    jades_path = '/vos/images/JADES/goods_s_F277W_2018_08_29.fits'

    jades_size = 9
    dc19_size = 9
    dc20_size = 9

    # hh_tstfyl = f"{TEST_RESOURCES_DIR}/HorseHead.fits"
    # m13_tstfyl = f"{TEST_RESOURCES_DIR}/m13.fits"

    imgr = ImageManager(test_args)          # instance of class under tests


    def test_setup_app (self, app):
        " Create an instance of the app: should be executed only once by conftest.py. "
        assert app is not None



    def test_cleanup(self, client):
        self.imgr.cleanup()
        assert True                         # nothing to test at the moment



    def test_image_metadata_badid(self):
        """ No record with given ID. """
        res = self.imgr.image_metadata(9999)
        print(res)
        assert res is None


    def test_image_metadata(self):
        """ Valid ID. """
        res = self.imgr.image_metadata(1)
        print(res)
        assert res is not None
        assert res['id'] == 1
        assert res['obs_collection'] == 'JADES'



    def test_image_metadata_by_collection_badcoll(self):
        """ No such collection. """
        res = self.imgr.image_metadata_by_collection(collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_collection(self):
        """ Valid collection. """
        res = self.imgr.image_metadata_by_collection(collection='JADES')
        print(res)
        assert res is not None
        assert len(res) == self.jades_size
        colls = [rec.get('obs_collection') for rec in res]
        print(colls)
        assert len(colls) == self.jades_size
        assert len(set(colls)) == 1



    def test_image_metadata_by_path_badpath(self):
        """ No image with given path. """
        res = self.imgr.image_metadata_by_path(self.bad_path)
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_path(self):
        """ Valid path. """
        res = self.imgr.image_metadata_by_path(self.dc19_path)
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('file_path') == self.dc19_path


    def test_image_metadata_by_path_badcoll(self):
        """ Path good but collection bad. """
        res = self.imgr.image_metadata_by_path(self.dc20_path, collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_path_goodcoll(self):
        """ Valid path. """
        res = self.imgr.image_metadata_by_path(self.dc20_path, collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('file_path') == self.dc20_path



    def test_image_metadata_by_filter_badfilt(self):
        """ No image with given filter. """
        res = self.imgr.image_metadata_by_filter('BADfilt')
        print(res)
        assert res is not None
        assert len(res) == 0


    def test_image_metadata_by_filter(self):
        """ Valid filter. """
        res = self.imgr.image_metadata_by_filter('F200W')
        print(res)
        assert res is not None
        assert len(res) == 3
        filtrecs = [rec.get('filter') for rec in res]
        print(filtrecs)
        assert len(set(filtrecs)) == 1


    def test_image_metadata_by_filter_badcoll(self):
        """ Path good but collection bad. """
        res = self.imgr.image_metadata_by_filter('F444W', collection='BADcoll')
        print(res)
        assert res is not None
        assert len(res) == 0



    def test_is_cutout_cached(self):
        assert self.imgr.is_cutout_cached('nosuch.fits', co_dir='/tmp') is False
        assert self.imgr.is_cutout_cached('m13.fits', co_dir=TEST_RESOURCES_DIR) is True



    def test_is_irods_file(self):
        assert self.imgr.is_irods_file('/not/an/iRods/filepath') is False
        assert self.imgr.is_irods_file(f"{IRODS_ZONE_NAME}/images/ok") is True
        assert self.imgr.is_irods_file(f"{IRODS_ZONE_NAME}/any/path/ok") is True



    def test_image_metadata_by_filter_goodcoll(self):
        """ Valid filter. """
        res = self.imgr.image_metadata_by_filter('F444W', collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('filter') == 'F444W'
        assert res[0].get('obs_collection') == 'DC20'



    def test_list_collections(self):
        lst = self.imgr.list_collections()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'DC19' in lst
        assert 'DC20' in lst
        assert 'JADES' in lst



    def test_list_filters(self):
        lst = self.imgr.list_filters()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert 'F090W' in lst
        assert 'F335M' in lst
        assert 'F444W' in lst


    def test_list_filters_goodcoll(self):
        lst = self.imgr.list_filters(collection='DC19')
        print(lst)
        assert lst is not None
        assert len(lst) == self.dc19_size
        assert 'F200W' in lst
        assert 'F356W' in lst
        assert 'F410M' in lst


    def test_list_filters_badcoll(self):
        lst = self.imgr.list_filters(collection='BADcoll')
        print(lst)
        assert lst is not None
        assert len(lst) == 0



    def test_list_image_paths(self):
        lst = self.imgr.list_image_paths()
        print(lst)
        assert lst is not None
        assert len(lst) > 0
        assert self.m13_path in lst
        assert self.dc19_path in lst
        assert self.dc20_path in lst


    def test_list_image_paths_goodcoll(self):
        lst = self.imgr.list_image_paths(collection='DC20')
        print(lst)
        assert lst is not None
        assert len(lst) == self.dc20_size
        assert self.dc20_path in lst


    def test_list_image_paths_badcoll(self):
        lst = self.imgr.list_image_paths(collection='BADcoll')
        print(lst)
        assert lst is not None
        assert len(lst) == 0



    def test_make_cutout_filename_min(self):
        co_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, co_args)
        print(fname)
        assert fname is not None
        assert fname == '_m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_min2(self):
        co_args = { 'ra': '53.157662568', 'dec': '-27.8075199236', 'size': '10', 'units': u.arcsec }
        fname = self.imgr.make_cutout_filename(self.jades_path, co_args)
        print(fname)
        assert fname is not None
        assert fname == '_goods_s_F277W_2018_08_29__53.157662568_-27.8075199236_10arcsec.fits'


    def test_make_cutout_filename_min3(self):
        co_args = { 'ra': '53.155277381023', 'dec': '-27.787295217953',
                    'size': '0.5', 'units': u.deg }
        fname = self.imgr.make_cutout_filename(self.dc20_path, co_args)
        print(fname)
        assert fname is not None
        assert fname == '_F356W__53.155277381023_-27.787295217953_0.5deg.fits'


    def test_make_cutout_filename_coll(self):
        co_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, co_args, collection='JADES')
        print(fname)
        assert fname is not None
        assert fname == 'JADES__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_filt(self):
        co_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, co_args, filt='AFILT')
        print(fname)
        assert fname is not None
        assert fname == 'AFILT__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_collNfilt(self):
        co_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, co_args, filt='AFILT', collection='JADES')
        print(fname)
        assert fname is not None
        assert fname == 'JADES_AFILT__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_CUTOUT_METHODS(self):
        co_dir = '/tmp'
        co_filename = f"_m13__250.4226_36.4602_1arcsec.fits"
        assert self.imgr.is_cutout_cached(co_filename, co_dir) is False
