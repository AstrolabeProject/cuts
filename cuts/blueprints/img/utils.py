#
# Module to provide general utility functions for Astrolabe code.
#   Written by: Tom Hicks. 7/26/2018.
#   Last Modified: Corrections from test suite.
#
import fnmatch
import os

# patterns for identifying FITS and gzipped FITS files
_FITS_PAT = "*.fits"
_GZFITS_PAT = "*.fits.gz"

# suffixes for identifying FITS and gzipped FITS files
_FITS_EXTENTS = [ '.fits', '.fits.gz' ]


def is_fits_file (fyl):
    """ Return True if the given file is FITS file, else False. """
    return (fnmatch.fnmatch(fyl, _FITS_PAT) or fnmatch.fnmatch(fyl, _GZFITS_PAT))


def is_fits_filename (filename, extents=_FITS_EXTENTS):
    """ Return True if the given filename string names a FITS file, else False. """
    return (filename.endswith(tuple(extents)))


def gen_file_paths (root_dir):
    """ Generator to yield all files in the file tree under the given root directory. """
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        for fyl in files:
            file_path = os.path.join(root, fyl)
            yield file_path


def get_metadata_keys (options):
    """
    Return a list of metadata keys to be extracted.

    throws FileNotFoundError is given a non-existant or unreadable filepath.
    """
    keyfile = options.get("keyfile")
    if (keyfile):
        with open(keyfile, "r") as mdkeys_file:
            return mdkeys_file.read().splitlines()
    else:
        return None


def path_has_dots (apath):
    """ Tell whether the given path contains '.' or '..' """
    pieces = apath.split(os.sep)
    return (('.' in pieces) or ('..' in pieces))
