import os
import pytest

from config.settings import FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS
import cuts.blueprints.img.image_manager as imgr
from cuts.blueprints.img import exceptions


class TestImageManager(object):

    acat = 'tests/resources/cats/small_table.fits'
    imgdir = 'tests/resources/pics'
    hh = 'tests/resources/pics/JADES/images/HorseHead.fits'
    hh_hdr = 'tests/resources/pics/JADES/images/hdr-HorseHead.txt'
    m13 = 'tests/resources/pics/m13.fits'
    m13_hdr = 'tests/resources/pics/hdr-m13.txt'
    m13_name = 'm13.fits'
    m13_deep_name = 'm13_2.fits'
    not_fits = 'empty.fits'
    nosuch_file = 'NOSUCHFILE'
    nosuch_path = 'tests/resources/NOSUCHFILE'
    vos_hh = '/vos/images/HorseHead.fits'
    vos_hh_deep = '/vos/images/JADES/HorseHead.fits'
    vos_m13 = '/vos/images/m13.fits'
    vos_m13_jades = '/vos/images/JADES/m13.fits'
    vos_m13_deep = '/vos/images/JADES/SubDir/m13_2.fits'


    def assert_metadata_valid(self, md, has_keys, has_not_keys, filepath):
        for key in has_keys:
            assert (key in md)
        for key in has_not_keys:
            assert (not key in md)
        assert (md.get('filepath') == filepath)


    def test_clear_cache(self):
        imgr.initialize_cache()
        assert len(imgr.IMAGE_MD_CACHE) != 0
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0


    def test_initialize_cache(self):
        # this also directly tests list_fits_paths
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0
        imgr.initialize_cache()
        assert len(imgr.IMAGE_MD_CACHE) != 0


    def test_refresh_cache(self):
        # this also directly tests list_fits_paths and get_metadata
        imgr.clear_cache()                  # start from scratch
        assert len(imgr.IMAGE_MD_CACHE) == 0
        imgr.refresh_cache()                # test initial storage path
        assert len(imgr.IMAGE_MD_CACHE) != 0
        imgr.refresh_cache()                # test update storage path
        assert len(imgr.IMAGE_MD_CACHE) != 0


    def test_refresh_cache_dirty(self):
        imgr.refresh_cache()                # setup cache
        assert len(imgr.IMAGE_MD_CACHE) != 0
        md = imgr.get_metadata(self.vos_m13) # get metadata
        md['timestamp'] = 2                 # reset timestamp to be very old
        imgr.put_metadata(md)               # replace the metadata
        imgr.refresh_cache()                # test update of stale cache entry
        assert len(imgr.IMAGE_MD_CACHE) != 0


    def test_by_filter_matcher(self):
        assert imgr.by_filter_matcher({}, {}) == False
        assert imgr.by_filter_matcher({'xxx':'nope'}, {}) == False
        assert imgr.by_filter_matcher({'FILTER':'F200W'}, {}) == False
        assert imgr.by_filter_matcher({'filter':'F200W'}, {}) == False
        assert imgr.by_filter_matcher({}, {'xxx':'nope'}) == False
        assert imgr.by_filter_matcher({}, {'FILTER':'F200W'}) == False
        assert imgr.by_filter_matcher({}, {'filter':'F200W'}) == False
        assert imgr.by_filter_matcher({'xxx':'nope'}, {'xxx':'nope'}) == False
        assert imgr.by_filter_matcher({'FILTER':'F200W'}, {'FILTER':'F200W'}) == False
        assert imgr.by_filter_matcher({'filter':'F200W'}, {'FILTER':'F200W'}) == False
        assert imgr.by_filter_matcher({'FILTER':'F200W'}, {'filter':'F200W'}) == False

        assert imgr.by_filter_matcher({'filter':'F200W'}, {'filter':'F200W'}) == True


    def test_cache_key_from_metadata(self):
        assert imgr.cache_key_from_metadata({}) == None
        assert imgr.cache_key_from_metadata({'xxx':'nope'}) == None
        assert imgr.cache_key_from_metadata({'FILEPATH': 'nope'}) == None
        assert imgr.cache_key_from_metadata({'filepath': ''}) == None

        assert imgr.cache_key_from_metadata({'filepath': 'filename'}) == 'filename'
        assert imgr.cache_key_from_metadata({'filepath': '/some/path/'}) == '/some/path/'


    def test_collection_from_dirpath(self):
        IMD = IMAGES_DIR
        assert imgr.collection_from_dirpath('') == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/')) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x')) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x/y/z/')) == ''

        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x')) == 'x'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'xx/yyy')) == 'xx/yyy'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z')) == 'x/y/z'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z/')) == 'x/y/z'

        assert imgr.collection_from_dirpath('', IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/'), IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x'), IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x/y/z/'), IMD) == ''

        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x'), IMD) == 'x'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'xx/yyy'), IMD) == 'xx/yyy'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z'), IMD) == 'x/y/z'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z/'), IMD) == 'x/y/z'

        IMD = self.imgdir
        assert imgr.collection_from_dirpath('', IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/'), IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x'), IMD) == ''
        assert imgr.collection_from_dirpath(os.path.join(IMD, '/x/y/z/'), IMD) == ''

        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x'), IMD) == 'x'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'xx/yyy'), IMD) == 'xx/yyy'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z'), IMD) == 'x/y/z'
        assert imgr.collection_from_dirpath(os.path.join(IMD, 'x/y/z/'), IMD) == 'x/y/z'


    def test_collection_from_filepath(self):
        IMD = IMAGES_DIR
        assert imgr.collection_from_filepath('') == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/')) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x')) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x/y/z/')) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x')) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'file.fits')) == ''

        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy')) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z')) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z/')) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy.fits')) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits')) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits/')) == 'x/y'

        assert imgr.collection_from_filepath('', IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x/y/z/'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'file.fits'), IMD) == ''

        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy'), IMD) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z/'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy.fits'), IMD) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits/'), IMD) == 'x/y'

        IMD = self.imgdir
        assert imgr.collection_from_filepath('', IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, '/x/y/z/'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x'), IMD) == ''
        assert imgr.collection_from_filepath(os.path.join(IMD, 'file.fits'), IMD) == ''

        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy'), IMD) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z/'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'xx/yyy.fits'), IMD) == 'xx'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits'), IMD) == 'x/y'
        assert imgr.collection_from_filepath(os.path.join(IMD, 'x/y/z.fits/'), IMD) == 'x/y'


    def test_extract_metadata(self):
        md = imgr.extract_metadata(self.m13)
        # self.assert_m13_metadata_valid(md)  # REMOVE LATER
        self.assert_metadata_valid(
            md,                                        # the metadata to test
            ['center', 'corners', 'timestamp', 'wcs'], # must have these keys
            ['collection', 'filter'],                  # must not have these keys
            self.m13)                                  # must match filepath


    def test_fetch_metadata(self):
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0
        md = imgr.fetch_metadata(self.m13)
        assert len(imgr.IMAGE_MD_CACHE) == 1
        self.assert_metadata_valid(
            md,                                        # the metadata to test
            ['center', 'corners', 'timestamp', 'wcs'], # must have these keys
            ['collection', 'filter'],                  # must not have these keys
            self.m13)                                  # must match filepath


    def test_fits_file_exists(self):
        assert imgr.fits_file_exists('tests/resources/pics') == False
        assert imgr.fits_file_exists(self.nosuch_path) == False
        assert imgr.fits_file_exists(self.m13_hdr) == False
        assert imgr.fits_file_exists(self.hh_hdr) == False

        assert imgr.fits_file_exists(self.m13) == True
        assert imgr.fits_file_exists(self.hh) == True
        assert imgr.fits_file_exists(self.acat) == True


    def test_gen_collection_names(self):
        cnames = [ coll for coll in imgr.gen_collection_names() ]
        assert len(cnames) > 0
        assert ('JADES' in cnames)
        assert ('JADES/SubDir' in cnames)
        assert ('DC_191217' in cnames)

        cnames = [ coll for coll in imgr.gen_collection_names(image_dir=self.imgdir) ]
        assert len(cnames) > 0
        assert ('JADES/images' in cnames)


    def test_get_metadata(self):
        imgr.refresh_cache()
        hhpath = os.path.join(IMAGES_DIR, 'HorseHead.fits')
        md = imgr.get_metadata(hhpath)
        self.assert_metadata_valid(
            md,                                                  # the metadata to test
            ['center', 'corners', 'filter', 'timestamp', 'wcs'], # must have these keys
            ['collection'],                                      # must not have these keys
            hhpath)                                              # must match filepath


    def test_image_contains(self):
        imgr.image_contains(self.hh, {'ra': '53.16', 'dec': '-27.78'}) == False
        imgr.image_contains(self.hh, {'ra': '85.274970', 'dec': '-2.458265'}) == True
        imgr.image_contains(self.hh, {'ra': '85.275000', 'dec': '-2.458300'}) == True


    def test_image_corners(self):
        corners = imgr.image_corners(self.hh)
        assert len(corners) != 0
        assert len(corners) == 4
        for i in range(3):
            assert len(corners[i]) == 2


    def test_image_dir_from_collection(self):
        coll = 'coll'
        goods = 'JADES/goods'
        pics = 'Pics'
        assert imgr.image_dir_from_collection() == IMAGES_DIR
        assert imgr.image_dir_from_collection(None) == IMAGES_DIR
        assert imgr.image_dir_from_collection(coll).startswith(IMAGES_DIR)
        assert imgr.image_dir_from_collection(coll).endswith(os.sep+coll)
        assert imgr.image_dir_from_collection(goods).startswith(IMAGES_DIR)
        assert imgr.image_dir_from_collection(goods).endswith(os.sep+goods)

        assert imgr.image_dir_from_collection(None, pics) == pics
        assert imgr.image_dir_from_collection(coll, pics).startswith(pics)
        assert imgr.image_dir_from_collection(coll, pics).endswith(os.sep+coll)
        assert imgr.image_dir_from_collection(goods, pics).startswith(pics)
        assert imgr.image_dir_from_collection(goods, pics).endswith(os.sep+goods)


    def test_is_image_file(self):
        # this also directly tests is_image_header
        assert imgr.is_image_file(self.imgdir) == False
        assert imgr.is_image_file(self.nosuch_path) == False
        assert imgr.is_image_file(self.acat) == False
        assert imgr.is_image_file(self.m13_hdr) == False
        assert imgr.is_image_file(self.hh_hdr) == False

        assert imgr.is_image_file(self.m13) == True
        assert imgr.is_image_file(self.hh) == True


    def test_list_collections(self):
        # this also directly tests gen_collection_names
        coll = imgr.list_collections()
        assert len(coll) > 0
        assert 'JADES' in coll


    def test_list_fits_paths(self):
        # already tested by calling methods
        assert True


    def test_match_image(self, app):
        bad_args =  { 'ra': '3.14159265', 'dec': '-2.71828' }
        m13_args =  { 'ra': '250.4200', 'dec': '36.4600' }
        hh_args =   { 'ra': '85.274970', 'dec': '-2.458265' }
        jade_args = { 'ra': '53.16', 'dec': '-27.78' }

        assert imgr.match_image(bad_args) == None
        assert imgr.match_image(bad_args, collection='JADES') == None
        assert imgr.match_image(hh_args, collection='JADES/SubDir') == None

        m13_match = imgr.match_image(m13_args)
        assert m13_match == self.vos_m13

        m13_match = imgr.match_image(m13_args, collection='JADES')
        assert m13_match == self.vos_m13_jades

        m13_match = imgr.match_image(m13_args, collection='JADES/SubDir')
        assert m13_match == self.vos_m13_deep

        hh_match = imgr.match_image(hh_args)
        assert hh_match == self.vos_hh

        hh_match = imgr.match_image(hh_args, collection='JADES')
        assert hh_match == self.vos_hh_deep

        jade_match = imgr.match_image(jade_args)
        assert jade_match.startswith('/vos/images/JADES')


    def test_match_image_byfilter(self, app):
        bad_args =  { 'ra': '3.14159265', 'dec': '-2.71828', 'filter': 'F444W' }
        m13_args =  { 'ra': '250.4200', 'dec': '36.4600', 'filter': 'F444W'  }
        hh_args =   { 'ra': '85.274970', 'dec': '-2.458265', 'filter': 'OG590'  }
        jade_args = { 'ra': '53.16', 'dec': '-27.78', 'filter': 'F444W' }

        assert imgr.match_image(bad_args, match_fn=imgr.by_filter_matcher) == None
        assert imgr.match_image(bad_args,
                                collection='JADES',
                                match_fn=imgr.by_filter_matcher) == None

        assert imgr.match_image(m13_args, match_fn=imgr.by_filter_matcher) == None
        assert imgr.match_image(m13_args,
                                collection='JADES',
                                match_fn=imgr.by_filter_matcher) == None
        assert imgr.match_image(m13_args,
                                collection='JADES/SubDir',
                                match_fn=imgr.by_filter_matcher) == None

        assert imgr.match_image(hh_args,
                                collection='JADES/SubDir',
                                match_fn=imgr.by_filter_matcher) == None

        hh_match = imgr.match_image(hh_args, match_fn=imgr.by_filter_matcher)
        assert hh_match == self.vos_hh

        hh_match = imgr.match_image(hh_args, collection='JADES', match_fn=imgr.by_filter_matcher)
        assert hh_match == self.vos_hh_deep

        jade_match = imgr.match_image(jade_args, match_fn=imgr.by_filter_matcher)
        assert jade_match == '/vos/images/JADES/goods_s_F444W_2018_08_31.fits'


    def test_metadata_contains(self):
        assert imgr.metadata_contains(None, None) == False
        assert imgr.metadata_contains({}, []) == False
        assert imgr.metadata_contains({'no wcs': 'fails'}, []) == False


    def test_put_metadata(self, app):
        # valid paths are also tested by calling methods
        assert imgr.put_metadata({}) == False
        assert imgr.put_metadata({'no_cache_key': 'fails'}) == False

        assert imgr.put_metadata({'filepath': self.m13}) == True
        md = { 'filepath': self.hh, 'collection':'Mine', 'filter':'F410M', 'timestamp':42 }
        assert imgr.put_metadata(md) == True


    def test_return_image(self, app, client):
        with pytest.raises(exceptions.ImageNotFound):
            imgr.return_image(self.nosuch_path)
        with pytest.raises(exceptions.ImageNotFound):
            imgr.return_image(self.nosuch_path, collection='bogus')

        with app.test_request_context():
            image = imgr.return_image(self.vos_m13)
            assert image != None
            assert type(image) == app.response_class
            assert image.status_code == 200
            hdrs = image.headers
            assert hdrs.get('Content-Length') == '184320'
            assert hdrs.get('Content-Type') == 'image/fits'
            assert (self.m13_name in hdrs.get('Content-Disposition'))


        with app.test_request_context():
            image = imgr.return_image(self.vos_m13_deep, collection='JADES/SubDir')
            assert image != None
            assert type(image) == app.response_class
            assert image.status_code == 200
            hdrs = image.headers
            assert hdrs.get('Content-Length') == '184320'
            assert hdrs.get('Content-Type') == 'image/fits'
            assert (self.m13_deep_name in hdrs.get('Content-Disposition'))


    def test_show_cache(self):
        imgr.refresh_cache()
        rep = imgr.show_cache()
        assert (rep and len(rep) > 0)


    def test_store_metadata(self):
        # test the problem paths: valid paths are already tested by calling methods
        assert imgr.store_metadata(self.not_fits) == None
        assert imgr.store_metadata(self.nosuch_file) == None
        assert imgr.store_metadata(self.nosuch_path) == None
        assert imgr.store_metadata(self.acat) == None
