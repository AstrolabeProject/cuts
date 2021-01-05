# Tests for the file utilities module.
#   Written by: Tom Hicks. 5/22/2020.
#   Last Modified: Port to Cuts.
#
import os
from pathlib import Path

import cuts.blueprints.img.file_utils as utils

from tests import TEST_DIR


class TestFileUtils(object):

    tmpPath = '/tmp'
    dirPath = '/tmp/MadeUpDIR'
    dirLink = '/tmp/linkToMadeUpDIR'
    fylPath = '/tmp/HiGhLy_UnLiKeLy'
    fylLink = '/tmp/linkToHiGhLy_UnLiKeLy'

    empty_tstfyl = "{}/resources/empty.txt".format(TEST_DIR)
    m13_tstfyl = "{}/resources/m13.fits".format(TEST_DIR)
    mdkeys_tstfyl = "{}/resources/mdkeys.txt".format(TEST_DIR)
    table_tstfyl = "{}/resources/small_table.fits".format(TEST_DIR)


    def test_filename_core(self):
        assert utils.filename_core(None) == ''
        assert utils.filename_core('') == ''
        assert utils.filename_core('/tmp') == 'tmp'
        assert utils.filename_core('/tmp/somefile') == 'somefile'
        assert utils.filename_core('/tmp/somefile.py') == 'somefile'


    def test_full_path(self):
        home = str(Path.home())
        assert utils.full_path('~') == home
        assert utils.full_path('~/.bashrc') == f'{home}/.bashrc'
        assert utils.full_path(self.tmpPath) == self.tmpPath
        assert utils.full_path('/tmp/somefile') == '/tmp/somefile'
        assert utils.full_path('/tmp/somefile.py') == '/tmp/somefile.py'


    def test_gen_file_paths(self):
        paths = [ p for p in utils.gen_file_paths(os.getcwd()) ]
        assert len(paths) != 0, "The generated path list for PWD is not empty."

        paths = [ p for p in utils.gen_file_paths(self.fylPath) ]
        assert len(paths) == 0, "The generated path list for non-existant directory is empty."


    def test_good_dir_path(self):
        # also tests is_readable
        assert utils.good_dir_path('dummy') is False
        assert utils.good_dir_path(self.fylPath) is False
        assert utils.good_dir_path(self.dirPath) is False

        assert utils.good_dir_path('.') is True
        assert utils.good_dir_path('/') is True
        assert utils.good_dir_path(self.tmpPath) is True

        # setup directories and links
        try:
            os.mkdir(self.dirPath, mode=0o444)
            dirp = Path(self.dirPath)
            dlnk = Path(self.dirLink)
            dlnk.symlink_to(dirp)

            assert utils.good_dir_path(self.dirPath) is True
            assert utils.good_dir_path(self.dirLink) is True
        finally:
            # cleanup directories and links
            os.rmdir(self.dirPath)
            os.remove(self.dirLink)


    def test_good_dir_path_write(self):
        # also tests is_writable
        assert utils.good_dir_path('dummy', True) is False
        assert utils.good_dir_path(self.fylPath, True) is False
        assert utils.good_dir_path(self.dirPath, True) is False

        assert utils.good_dir_path('.', True) is True
        assert utils.good_dir_path(self.tmpPath, True) is True

        try:
            # setup directories and links
            os.mkdir(self.dirPath, mode=0o775)
            dirp = Path(self.dirPath)
            dlnk = Path(self.dirLink)
            dlnk.symlink_to(dirp)

            assert utils.good_dir_path(self.dirPath) is True
            assert utils.good_dir_path(self.dirPath, True) is True
            assert utils.good_dir_path(self.dirLink) is True
            assert utils.good_dir_path(self.dirLink, True) is True

        finally:
            # cleanup directories and links
            os.rmdir(self.dirPath)
            os.remove(self.dirLink)


    def test_good_file_path(self):
        # also tests is_readable
        assert utils.good_file_path('.') is False
        assert utils.good_file_path('/') is False
        assert utils.good_file_path(self.tmpPath) is False
        assert utils.good_file_path('dummy') is False
        assert utils.good_file_path('/dummy') is False
        assert utils.good_file_path('/images/JADES/NONE.fits') is False

        # setup files and links
        fylp = Path(self.fylPath)
        fylp.touch(mode=0o444)
        flnk = Path(self.fylLink)
        flnk.symlink_to(fylp)               # ln -s fylPath fylLink

        assert utils.good_file_path(self.fylPath) is True
        assert utils.good_file_path(self.fylLink) is True

        # cleanup directories and links
        os.remove(self.fylPath)
        os.remove(self.fylLink)


    def test_good_file_path_write(self):
        # also tests is_writable
        assert utils.good_file_path('.', True) is False
        assert utils.good_file_path('/', True) is False
        assert utils.good_file_path('dummy') is False
        assert utils.good_file_path(self.tmpPath, True) is False
        assert utils.good_file_path(self.fylPath) is False
        assert utils.good_file_path(self.fylLink) is False

        # setup files and links
        fylp = Path(self.fylPath)
        fylp.touch(mode=0o444)
        flnk = Path(self.fylLink)
        flnk.symlink_to(fylp)               # ln -s fylPath fylLink

        assert utils.good_file_path(self.fylPath) is True
        assert utils.good_file_path(self.fylLink) is True

        # cleanup directories and links
        os.remove(self.fylPath)
        os.remove(self.fylLink)


    def test_is_acceptable_filename(self):
        FITS_EXTS = ['.fits', '.fits.gz']
        assert utils.is_acceptable_filename('.fits', FITS_EXTS) is True
        assert utils.is_acceptable_filename('.fits.fits', FITS_EXTS) is True
        assert utils.is_acceptable_filename('x.fits', FITS_EXTS) is True
        assert utils.is_acceptable_filename('X.Y.fits', FITS_EXTS) is True
        assert utils.is_acceptable_filename('XXX-YYY_.fits', FITS_EXTS) is True
        assert utils.is_acceptable_filename('.fits.gz', FITS_EXTS) is True
        assert utils.is_acceptable_filename('.fits.fits.gz', FITS_EXTS) is True
        assert utils.is_acceptable_filename('x.fits.gz', FITS_EXTS) is True
        assert utils.is_acceptable_filename('X.Y.fits.gz', FITS_EXTS) is True
        assert utils.is_acceptable_filename('XXX-YYY_.fits.gz', FITS_EXTS) is True

        assert utils.is_acceptable_filename('.', FITS_EXTS) is False
        assert utils.is_acceptable_filename('.fitsy', FITS_EXTS) is False
        assert utils.is_acceptable_filename('.fits.fitsy', FITS_EXTS) is False
        assert utils.is_acceptable_filename('fits', FITS_EXTS) is False
        assert utils.is_acceptable_filename('fits.gz', FITS_EXTS) is False
        assert utils.is_acceptable_filename('X.fit', FITS_EXTS) is False
        assert utils.is_acceptable_filename('X.fitsgz', FITS_EXTS) is False
        assert utils.is_acceptable_filename('bad.fits_gz', FITS_EXTS) is False
        assert utils.is_acceptable_filename('yyy.exe', FITS_EXTS) is False
        assert utils.is_acceptable_filename('YYY.EXE', FITS_EXTS) is False
        assert utils.is_acceptable_filename('BAD.ONE', FITS_EXTS) is False
        assert utils.is_acceptable_filename('BAD.ONE.gz', FITS_EXTS) is False


    def test_path_has_dots(self):
        assert utils.path_has_dots('.') is True
        assert utils.path_has_dots('..') is True
        assert utils.path_has_dots('./..') is True
        assert utils.path_has_dots('./usr/dummy/') is True
        assert utils.path_has_dots('../usr/dummy/') is True
        assert utils.path_has_dots('/usr/dummy/./smarty') is True
        assert utils.path_has_dots('/usr/dummy/../smarty') is True
        assert utils.path_has_dots('/usr/dummy/.') is True
        assert utils.path_has_dots('/usr/dummy/..') is True

        assert utils.path_has_dots(None) is False
        assert utils.path_has_dots('') is False
        assert utils.path_has_dots('dummy') is False
        assert utils.path_has_dots('dummy.txt') is False
        assert utils.path_has_dots('dummy.file.txt') is False
        assert utils.path_has_dots('/') is False
        assert utils.path_has_dots('/dummy') is False
        assert utils.path_has_dots('/usr/dummy') is False
        assert utils.path_has_dots('/usr/dummy/') is False


    def test_validate_path_strings(self):
        FILE_EXTENTS = ['.txt']
        testpaths = [ '.', '/', '/NoSuch',
                      self.tmpPath,
                      '/tmp/NoSuch',
                      self.empty_tstfyl,
                      self.m13_tstfyl,
                      '/images/JADES/NONE.fits',
                      '', None ]
        pathlst = utils.validate_path_strings(testpaths, FILE_EXTENTS)
        print("PATHLIST={}".format(pathlst))
        assert len(pathlst) == 4
        assert self.tmpPath in pathlst
        assert self.empty_tstfyl in pathlst
        assert self.m13_tstfyl not in pathlst
        assert '/images/JADES/NONE.fits' not in pathlst


    def test_validate_path_strings_fits(self):
        FITS_EXTENTS = ['.fits', '.fits.gz']
        testpaths = [ '.', '/', '/NoSuch',
                      self.tmpPath,
                      '/tmp/NoSuch',
                      self.empty_tstfyl,
                      self.m13_tstfyl,
                      '/images/JADES/NONE.fits',
                      '', None ]
        pathlst = utils.validate_path_strings(testpaths, FITS_EXTENTS)
        print("PATHLIST={}".format(pathlst))
        assert len(pathlst) == 4
        assert self.tmpPath in pathlst
        assert self.m13_tstfyl in pathlst
        assert '/images/JADES/NONE.fits' not in pathlst
        assert self.empty_tstfyl not in pathlst
