# Tests of the FITS specific utilities module.
#   Written by: Tom Hicks. 4/7/2020.
#   Last Modified: Sync with updated tests from imdtoolkit project.
#
import json
import pytest

from astropy import wcs
from astropy.table import Table
from astropy.time.core import Time
from astropy.io import fits

import cuts.blueprints.img.fits_utils as utils
from tests import TEST_RESOURCES_DIR


class TestFitsUtils(object):

    empty_tstfyl  = f"{TEST_RESOURCES_DIR}/empty.txt"
    hh_tstfyl     = f"{TEST_RESOURCES_DIR}/HorseHead.fits"
    m13_tstfyl    = f"{TEST_RESOURCES_DIR}/m13.fits"
    mdkeys_tstfyl = f"{TEST_RESOURCES_DIR}/mdkeys.txt"
    table_tstfyl  = f"{TEST_RESOURCES_DIR}/small_table.fits"


    def test_fits_file_exist(self):
        assert utils.fits_file_exists('/tmp/nosuchfile.txt') is False
        assert utils.fits_file_exists('/tmp/nosuchfile.fits') is False
        assert utils.fits_file_exists(self.m13_tstfyl) is True



    # TODO: update tests when better implementation is used (see tested code for details):
    def test_fits_utc_date_utc(self):
        tym = utils.fits_utc_date('1990-12-22T13:49:00')
        print(tym)
        assert tym is not None
        assert type(tym) == Time


    def test_fits_utc_date_ymd(self):
        tym = utils.fits_utc_date('2018-08-25')
        print(tym)
        assert tym is not None
        assert type(tym) == Time


    def test_fits_utc_date_yearonly(self):
        tym = None
        with pytest.raises(ValueError):
            tym = utils.fits_utc_date('1990')
        print(tym)
        assert tym is None



    def test_gen_fits_file_paths(self):
        ffs = [ f for f in utils.gen_fits_file_paths(TEST_RESOURCES_DIR) ]
        print(ffs)
        assert len(ffs) > 0
        assert self.m13_tstfyl in ffs


    def test_gen_fits_file_paths_empty(self):
        ffs = [ f for f in utils.gen_fits_file_paths('/tmp')]
        print(ffs)
        assert len(ffs) == 0
        assert self.m13_tstfyl not in ffs



    def test_get_column_info(self):
        with fits.open(self.table_tstfyl) as hdus:
            col_info = utils.get_column_info(hdus)
            assert col_info is not None


    def test_get_column_info_good_hdu(self):
        with fits.open(self.table_tstfyl) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=1)
            assert col_info is not None


    def test_get_column_info_no_table(self):
        with fits.open(self.m13_tstfyl) as hdus:
            col_info = utils.get_column_info(hdus)
            assert col_info is None


    def test_get_column_info_bad_low_hdu(self):
        with fits.open(self.table_tstfyl) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=0)
            assert col_info is None


    def test_get_column_info_bad_high_hdu(self):
        with fits.open(self.table_tstfyl) as hdus:
            col_info = utils.get_column_info(hdus, which_hdu=2)
            assert col_info is None



    def test_get_header_fields_default(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus)

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided, comments removed
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' not in hdrs        # removed by default


    def test_get_header_fields_indexed(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus, 0)

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided, comments removed
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' not in hdrs        # removed by default


    def test_get_header_fields_badindex(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus, 1)  # no HDU at index 1
        assert hdrs is None


    def test_get_header_fields_ignore_key(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=['SIMPLE', ''])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 18              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' not in hdrs         # removed explicitly
        assert 'COMMENT' in hdrs            # should not be removed


    def test_get_header_fields_ignore_min(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=[''])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' in hdrs            # should not be removed


    def test_get_header_fields_ignore_empty(self):
        hdrs = None
        with fits.open(self.m13_tstfyl) as hdus:
            hdrs = utils.get_header_fields(hdus, ignore=[])

        print(hdrs)
        assert hdrs is not None
        assert len(hdrs) > 0
        assert len(hdrs) == 19              # really 25 but duplicates elided
        assert 'CTYPE1' in hdrs
        assert 'SIMPLE' in hdrs
        assert 'COMMENT' in hdrs            # should not be removed



    def test_get_image_corners(self):
        corners = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            corners = utils.get_image_corners(wcs_info)
        print(corners)
        assert len(corners) == 4
        for idx, c in enumerate(corners):
            assert len(corners[idx]) == 2



    def test_get_image_scale(self):
        scale = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs_info = wcs.WCS(hdus[0].header)
            scale = utils.get_image_scale(wcs_info)
        print(scale)
        assert len(scale) > 0
        assert len(scale) == 2
        assert scale[0] > 0



    def test_get_WCS_default(self):
        wcs = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs = utils.get_WCS(hdus)
        assert wcs is not None


    def test_get_WCS_indexed(self):
        wcs = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs = utils.get_WCS(hdus, 0)
        assert wcs is not None


    def test_get_WCS_badindex(self):
        wcs = None
        with fits.open(self.m13_tstfyl) as hdus:
            wcs = utils.get_WCS(hdus, 1)   # no HDU at index 1
        assert wcs is None



    def test_has_catalog_data_default(self):
        """ Check default HDU of catalog file for catalog data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus) is True


    def test_has_catalog_data_good_hdu(self):
        """ Check explicit HDU of catalog file for catalog data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus, which_hdu=1) is True


    def test_has_catalog_data_nonex_hdu(self):
        """ Check non-existant extension of image file for catalog data. """
        with fits.open(self.m13_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus) is False


    def test_has_catalog_data_bad_low_hdu(self):
        """ Check primary HDU of catalog file for catalog data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus, which_hdu=0) is False


    def test_has_catalog_data_bad_high_hdu(self):
        """ Check non-existant extension of catalog file for catalog data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus, which_hdu=2) is False


    def test_has_catalog_data_mixed_primary(self):
        """ Check primary of mixed image/cat file for image data. """
        with fits.open(self.hh_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus, which_hdu=0) is False


    def test_has_catalog_data_mixed(self):
        """ Check catalog extension of mixed image/cat file for image data. """
        with fits.open(self.hh_tstfyl) as hdus:
            assert utils.has_catalog_data(hdus) is True



    def test_has_image_data(self):
        """ Check primary of catalog file for image data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_image_data(hdus) is False


    def test_has_image_data_cat(self):
        """ Check catalog extension of catalog file for image data. """
        with fits.open(self.table_tstfyl) as hdus:
            assert utils.has_image_data(hdus, which_hdu=1) is False


    def test_has_image_data_good(self):
        """ Check primary of image file for image data. """
        with fits.open(self.m13_tstfyl) as hdus:
            assert utils.has_image_data(hdus) is True


    def test_has_image_data_bad_high_hdu(self):
        """ Check non-existant extension of image file for image data. """
        with fits.open(self.m13_tstfyl) as hdus:
            assert utils.has_image_data(hdus, which_hdu=1) is False


    def test_has_image_data_mixed(self):
        """ Check primary (default) of mixed image/cat file for image data. """
        with fits.open(self.hh_tstfyl) as hdus:
            assert utils.has_image_data(hdus) is True


    def test_has_image_data_mixed_cat(self):
        """ Check catalog extension of mixed image/cat file for image data. """
        with fits.open(self.hh_tstfyl) as hdus:
            assert utils.has_image_data(hdus, which_hdu=1) is False



    def test_is_fits_file(self):
        assert utils.is_fits_file('m13.fits') is True
        assert utils.is_fits_file('m13.fits.gz') is True
        assert utils.is_fits_file('/usr/dummy/m13.fits') is True
        assert utils.is_fits_file('/usr/dummy/m13.fits.gz') is True

        assert utils.is_fits_file('m13') is False
        assert utils.is_fits_file('m13-fits') is False
        assert utils.is_fits_file('m13.gz') is False
        assert utils.is_fits_file('/usr/dummy/m13') is False
        assert utils.is_fits_file('/usr/dummy/m13-fits') is False
        assert utils.is_fits_file('/usr/dummy/m13.gz') is False


    def test_is_fits_filename(self):
        assert utils.is_fits_filename('m13.fits') is True
        assert utils.is_fits_filename('m13.fits.gz') is True
        assert utils.is_fits_filename('/usr/dummy/m13.fits') is True
        assert utils.is_fits_filename('/usr/dummy/m13.fits.gz') is True

        assert utils.is_fits_filename('m13') is False
        assert utils.is_fits_filename('m13.gz') is False
        assert utils.is_fits_filename('m13-fits') is False
        assert utils.is_fits_filename('/usr/dummy/m13') is False
        assert utils.is_fits_filename('/usr/dummy/m13-fits') is False
        assert utils.is_fits_filename('/usr/dummy/m13.gz') is False



    def test_metadata_keys(self):
        assert utils.get_metadata_keys({}) is None
        assert utils.get_metadata_keys({'keymissing': True}) is None
        assert utils.get_metadata_keys({'keyfile': None}) is None

        mdkeys = utils.get_metadata_keys({'keyfile': self.empty_tstfyl})
        assert len(mdkeys) == 0

        mdkeys = utils.get_metadata_keys({'keyfile': self.mdkeys_tstfyl})
        assert len(mdkeys) == 13

        with pytest.raises(FileNotFoundError):
            utils.get_metadata_keys({'keyfile': 'bad_filename'})


    def test_lookup_pixtype(self):
        assert utils.lookup_pixtype(0) == 'UNKNOWN'
        assert utils.lookup_pixtype('0') == 'UNKNOWN'
        assert utils.lookup_pixtype(1) == 'UNKNOWN'
        assert utils.lookup_pixtype('1') == 'UNKNOWN'
        assert utils.lookup_pixtype(-1) == 'UNKNOWN'
        assert utils.lookup_pixtype('-1') == 'UNKNOWN'
        assert utils.lookup_pixtype(100, 'NOT_FOUND') == 'NOT_FOUND'
        assert utils.lookup_pixtype('100', 'NOT_FOUND') == 'NOT_FOUND'
        assert utils.lookup_pixtype('BAD', 'BAD') == 'BAD'

        assert utils.lookup_pixtype(8) == 'byte'
        assert utils.lookup_pixtype('8') == 'byte'
        assert utils.lookup_pixtype(16) == 'short'
        assert utils.lookup_pixtype('16') == 'short'
        assert utils.lookup_pixtype(32) == 'int'
        assert utils.lookup_pixtype('32') == 'int'
        assert utils.lookup_pixtype(64) == 'long'
        assert utils.lookup_pixtype('64') == 'long'
        assert utils.lookup_pixtype(-32) == 'float'
        assert utils.lookup_pixtype('-32') == 'float'
        assert utils.lookup_pixtype(-64) == 'double'
        assert utils.lookup_pixtype('-64') == 'double'



    def test_rows_from_data(self):
        with fits.open(self.table_tstfyl) as hdus_list:
            fits_rec = hdus_list[1].data
            data = utils.rows_from_data(fits_rec)
            assert data is not None
            assert len(data) == 326         # number of data rows in test file



    def test_get_table_meta_attribute(self):
        with fits.open(self.table_tstfyl) as hdus_list:
            table = Table.read(hdus_list, hdu=1)
            meta = utils.get_table_meta_attribute(table)
            print(meta)
            assert meta is not None
            assert len(meta) == 4
            assert 'EXTNAME' in meta
            assert 'DATE-HDU' in meta


    def test_get_table_meta_attribute_nometa(self):
        with fits.open(self.table_tstfyl) as hdus_list:
            table = Table.read(hdus_list, hdu=1)
            table.meta = None
            meta = utils.get_table_meta_attribute(table)
            assert meta is not None
            assert meta == {}



    # def test_table_to_JSON(self):
    #     """
    #     Test writing a small FITS table out as JSON.
    #     NB: These tests are SPECIFIC to the test table file (small_table.fits).
    #     """
    #     tbl = Table.read(self.table_tstfyl, hdu=1)
    #     print(tbl)

    #     jtbl = utils.table_to_JSON(tbl)
    #     assert jtbl is not None
    #     print("LEN_JTBL={}".format(len(jtbl)))
    #     print("JTBL={}".format(jtbl))
    #     assert len(jtbl) > 40000            # specific to this test file

    #     pytbl = json.loads(jtbl)            # read JSON in
    #     print('TYPE(pytble)=', type(pytbl))
    #     print(pytbl)
    #     assert pytbl is not None
    #     print("LEN_PYTBL={}".format(len(pytbl)))
    #     assert len(pytbl) == 326            # specific to this test file
