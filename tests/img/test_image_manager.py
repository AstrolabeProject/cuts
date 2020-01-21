import cuts.blueprints.img.image_manager as imgr

import os
# import sys
import pytest

class TestUtils(object):

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
            return True


        def test_collection_from_filepath(self):
            return True


        def test_extract_metadata(self):
            return True


        def test_fetch_metadata(self):
            return True


        def test_fits_file_exists(self):
            return True


        def test_gen_collection_names(self):
            return True


        def test_get_metadata(self):
            return True


        def test_image_dir_from_collection(self):
            return True


        def test_is_image_file(self):
            return True


        def test_is_image_header(self):
            return True


        def test_list_collections(self):
            return True


        def test_list_fits_paths(self):
            return True


        def test_metadata_contains(self):
            return True


        def test_put_metadata(self):
            return True


        def test_return_image(self):
            return True


        def test_store_metadata(self):
            return True

