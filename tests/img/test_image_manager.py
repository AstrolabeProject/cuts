# Tests for the image manager module.
#   Written by: Tom Hicks. 1/9/2021.
#   Last Modified: Trivial resorting.
#
import os
import pytest

from flask import current_app, request, send_from_directory

from astropy import units as u
from astropy.io import fits
from astropy.nddata import Cutout2D

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError, NotYetImplemented
from cuts.blueprints.img.image_manager import DEFAULT_CUTOUTS_DIR, IRODS_ZONE_NAME, ImageManager
from cuts.blueprints.img.arg_utils import parse_cutout_args
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
    irods_path = '/iplant/fake/nosuchfile.fits'

    jades_size = 9
    dc19_size = 9
    dc20_size = 9

    no_overlap_emsg = "There is no overlap between the reference image and the given center coordinate:.*"
    retimg_emsg = "iRods connection capabilities not yet implemented."
    write_co_emsg = ".* Unexpected error while writing image cutout to cache file.*"

    # empty_tstfyl  = f"{TEST_RESOURCES_DIR}/empty.txt"
    hh_tstfyl     = f"{TEST_RESOURCES_DIR}/HorseHead.fits"
    m13_tstfyl    = f"{TEST_RESOURCES_DIR}/m13.fits"
    # table_tstfyl  = f"{TEST_RESOURCES_DIR}/small_table.fits"

    m13_co_args = parse_cutout_args({'ra':'250.4226', 'dec':'36.4602', 'sizeArcSec':'12'},
                                    required=True)
    m13_co_filename = f"_m13__250.4226_36.4602_12.0arcsec.fits"


    imgr = ImageManager(test_args)          # instance of class under tests


    def test_setup_app (self, app):
        " Create an instance of the app: should be executed only once by conftest.py. "
        assert app is not None



    def test_cleanup(self, client):
        self.imgr.cleanup()
        assert True                         # nothing to test at the moment



    def test_get_cutout(self, app):
        with app.test_request_context('/'):
            assert self.imgr.is_cutout_cached(self.m13_co_filename) is False  # not cached
            cout = self.imgr.get_cutout(self.m13_tstfyl, self.m13_co_args)
            assert cout is not None
            assert cout.status_code == 200
            assert cout.is_streamed is True

            print(os.listdir(DEFAULT_CUTOUTS_DIR))
            assert self.imgr.is_cutout_cached(self.m13_co_filename) is True  # cached now

            cout2 = self.imgr.get_cutout(self.m13_tstfyl, self.m13_co_args)  # get it again
            assert cout2 is not None
            assert cout2.status_code == 200
            assert cout2.is_streamed is True

            assert self.imgr.is_cutout_cached(self.m13_co_filename) is True  # still cached
            os.remove(os.path.join(DEFAULT_CUTOUTS_DIR, self.m13_co_filename))  # cleanup



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


    def test_image_metadata_by_filter_goodcoll(self):
        """ Valid filter. """
        res = self.imgr.image_metadata_by_filter('F444W', collection='DC20')
        print(res)
        assert res is not None
        assert len(res) == 1
        assert res[0].get('filter') == 'F444W'
        assert res[0].get('obs_collection') == 'DC20'



    def test_is_cutout_cached(self):
        assert self.imgr.is_cutout_cached('nosuch.fits', co_dir='/tmp') is False
        assert self.imgr.is_cutout_cached('m13.fits', co_dir=TEST_RESOURCES_DIR) is True



    def test_is_irods_file(self):
        assert self.imgr.is_irods_file('/not/an/iRods/filepath') is False
        assert self.imgr.is_irods_file(f"{IRODS_ZONE_NAME}/images/ok") is True
        assert self.imgr.is_irods_file(f"{IRODS_ZONE_NAME}/any/path/ok") is True



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



    def test_make_cutout(self, app):
        with app.test_request_context('/'):
            with fits.open(self.m13_tstfyl) as hdus:
                cout = self.imgr.make_cutout(hdus[0], self.m13_co_args)
                print(cout)
                assert cout is not None
                assert isinstance(cout, Cutout2D) is True
                print(f"original={cout.xmax_original}, {cout.ymax_original}")
                print(f"cutout={cout.xmax_cutout}, {cout.ymax_cutout}")
                assert cout.xmax_cutout < cout.xmax_original
                assert cout.ymax_cutout < cout.ymax_original



    def test_make_cutout_and_save_m13(self, app):
        with app.test_request_context('/'):
            co_filename = "testMakeCutoutAndSave.fits"
            assert self.imgr.is_cutout_cached(co_filename) is False    # not cached
            self.imgr.make_cutout_and_save(self.m13_tstfyl, self.m13_co_args, co_filename)
            print(os.listdir(DEFAULT_CUTOUTS_DIR))
            assert self.imgr.is_cutout_cached(co_filename) is True     # cached now
            os.remove(os.path.join(DEFAULT_CUTOUTS_DIR, co_filename))  # cleanup


    def test_make_cutout_and_save_m13_no_overlap(self, app):
        with app.test_request_context('/'):
            disjoint_co_args = parse_cutout_args({'ra':'18.0', 'dec':'4.0', 'sizeArcSec':'10'},
                                            required=True)
            print(f"CO_ARGS={disjoint_co_args}")
            co_filename = "shouldnotexist.fits"

            assert self.imgr.is_cutout_cached(co_filename) is False  # not cached
            with pytest.raises(RequestException, match=self.no_overlap_emsg) as reqex:
                self.imgr.make_cutout_and_save(self.hh_tstfyl, disjoint_co_args, co_filename)
            print(os.listdir(DEFAULT_CUTOUTS_DIR))
            assert self.imgr.is_cutout_cached(co_filename) is False  # still not cached


    def test_make_cutout_and_save_write_error(self, app):
        with app.test_request_context('/'):
            with pytest.raises(ServerError, match=self.write_co_emsg) as srverr:
                self.imgr.make_cutout_and_save(self.m13_tstfyl, self.m13_co_args, 'nofile', '/NONE')



    def test_make_cutout_filename_min(self):
        tst_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, tst_args)
        print(fname)
        assert fname is not None
        assert fname == '_m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_min2(self):
        tst_args = { 'ra': '53.157662568', 'dec': '-27.8075199236', 'size': '10', 'units': u.arcsec }
        fname = self.imgr.make_cutout_filename(self.jades_path, tst_args)
        print(fname)
        assert fname is not None
        assert fname == '_goods_s_F277W_2018_08_29__53.157662568_-27.8075199236_10arcsec.fits'


    def test_make_cutout_filename_min3(self):
        tst_args = { 'ra': '53.155277381023', 'dec': '-27.787295217953',
                    'size': '0.5', 'units': u.deg }
        fname = self.imgr.make_cutout_filename(self.dc20_path, tst_args)
        print(fname)
        assert fname is not None
        assert fname == '_F356W__53.155277381023_-27.787295217953_0.5deg.fits'


    def test_make_cutout_filename_coll(self):
        tst_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, tst_args, collection='JADES')
        print(fname)
        assert fname is not None
        assert fname == 'JADES__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_filt(self):
        tst_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, tst_args, filt='AFILT')
        print(fname)
        assert fname is not None
        assert fname == 'AFILT__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_make_cutout_filename_collNfilt(self):
        tst_args = { 'ra': '250.4226', 'dec': '36.4602', 'size': '2.4', 'units': u.arcmin }
        fname = self.imgr.make_cutout_filename(self.m13_path, tst_args, filt='AFILT', collection='JADES')
        print(fname)
        assert fname is not None
        assert fname == 'JADES_AFILT__m13__250.4226_36.4602_2.4arcmin.fits'


    def test_return_image_at_path_irods(self):
        """ iRods connections are not yet implemented. """
        with pytest.raises(NotYetImplemented, match=self.retimg_emsg) as nyi:
            self.imgr.return_image_at_path(self.irods_path)


    def test_return_image_at_path(self, app):
        """ Return a small image from the test resources directory. """
        with app.test_request_context('/'):
            img = self.imgr.return_image_at_path(self.m13_path)
            print(img)
            assert img is not None
            assert img.status_code == 200
            assert img.is_streamed is True
