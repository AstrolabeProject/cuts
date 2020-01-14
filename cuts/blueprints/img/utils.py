#
# Module to provide general utility functions for Astrolabe code.
#   Written by: Tom Hicks. 7/26/2018.
#   Last Modified: Add test for fits filename. Generalize method to file path generator.
#
import fnmatch
import os
import pathlib as pl

# patterns for identifying FITS and gzipped FITS files
_FITS_PAT = "*.fits"
_GZFITS_PAT = "*.fits.gz"


def is_fits_file (fyl):
    """ Return True if the given file is FITS file, else False. """
    return (fnmatch.fnmatch(fyl, _FITS_PAT) or fnmatch.fnmatch(fyl, _GZFITS_PAT))

def is_fits_filename (filename, extents):
    """ Return True if the given filename string names a FITS file, else False. """
    return (filename.endswith(tuple(extents)))


def gen_file_paths (root_dir):
    """ Generator to yield all files in the file tree under the given root directory. """
    for root, dirs, files in os.walk(root_dir, followlinks=True):
        for fyl in files:
            file_path = os.path.join(root, fyl)
            yield file_path


def get_metadata_keys (options):
    """ Return a list of metadata keys to be extracted. """
    keyfile = options.get("keyfile")
    if (keyfile):
        with open(keyfile, "r") as mdkeys_file:
            return mdkeys_file.read().splitlines()
    else:
        return None


def path_has_dots (apath):
    """ Tell whether the given path contains '.' or '..' """
    parts = list(pl.PurePath(apath).parts)
    return ((apath == ".") or (".." in parts) or ("." in parts))
