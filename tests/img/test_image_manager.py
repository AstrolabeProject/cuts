import os
import pytest

import cuts.blueprints.img.image_manager as imgr
from config.settings import FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS

class TestImageManager(object):

    imgdir = 'tests/resources/pics'
    m13 = 'tests/resources/pics/m13.fits'
    m13_hdr = 'tests/resources/pics/hdr-m13.txt'
    hh = 'tests/resources/pics/JADES/images/HorseHead.fits'
    hh_hdr = 'tests/resources/pics/JADES/images/hdr-HorseHead.txt'

    def test_clear_cache(self):
        imgr.initialize_cache()
        assert len(imgr.IMAGE_MD_CACHE) != 0
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0


    def test_initialize_cache(self):
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0
        imgr.initialize_cache()
        assert len(imgr.IMAGE_MD_CACHE) != 0


    def test_refresh_cache(self):
        imgr.clear_cache()
        assert len(imgr.IMAGE_MD_CACHE) == 0
        imgr.refresh_cache()
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
        assert len(md) != 0
        assert ('center' in md)
        assert (not 'collection' in md)
        assert ('corners' in md)
        assert (not 'filter' in md)
        assert (md.get('filepath') == self.m13)
        assert ('timestamp' in md)
        assert ('wcs' in md)


    def test_fetch_metadata(self):
        assert True


    def test_fits_file_exists(self):
        assert imgr.fits_file_exists('tests/resources/pics') == False
        assert imgr.fits_file_exists('tests/resources/NOSUCHFILE') == False
        assert imgr.fits_file_exists(self.m13_hdr) == False
        assert imgr.fits_file_exists(self.hh_hdr) == False

        assert imgr.fits_file_exists(self.m13) == True
        assert imgr.fits_file_exists(self.hh) == True


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
        assert len(md) != 0
        assert ('center' in md)
        assert (not 'collection' in md)
        assert ('corners' in md)
        assert ('filter' in md)
        assert (md.get('filepath') == hhpath)
        assert ('timestamp' in md)
        assert ('wcs' in md)


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
        assert imgr.is_image_file('tests/resources/pics') == False
        assert imgr.is_image_file('tests/resources/NOSUCHFILE') == False
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
        assert True


    def test_metadata_contains(self):
        assert True


    def test_put_metadata(self):
        assert True


    def test_return_image(self):
        assert True


    def test_store_metadata(self):
        assert True
