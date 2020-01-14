#
# Module to manage an in-memory image cache containing metadata from
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Updates for using filepaths instead of filenames.
#
import os

from flask import current_app, request

from config.settings import FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

import cuts.blueprints.img.utils as utils


# The metadata cache
IMAGE_MD_CACHE = {}


def clear_cache ():
    """Clear all entries in the metadata cache."""
    IMAGE_MD_CACHE = {}
    # current_app.logger.error("(clear_cache): CACHE: {}".format(IMAGE_MD_CACHE))


def initialize_cache ():
    """Initialize metadata cache with data from all FITS files in the image directory."""
    clear_cache()
    for filepath in list_fits_paths():
        store_metadata(filepath)
    # current_app.logger.error("(initialize_cache): CACHE: {}".format(IMAGE_MD_CACHE))


def refresh_cache ():
    """Refresh the metadata cache with data from any new or changed FITS files
       found in the image directory."""
    for filepath in list_fits_paths():
        md = get_metadata(filepath)         # try to get metadata for file
        if (not md):                        # metadata not found in cache
            store_metadata(filepath)        # so add it to cache
        else:                               # metadata was found: check if stale
            ctime = md['timestamp']         # timestamp of data in cache
            ftime = os.path.getmtime(filepath) # modification time on file
            if (ftime > ctime):             # if cache data is stale
                store_metadata(filepath)    # update the cache


def by_filter_matcher (co_args, metadata):
    """A matching function to match images with filters by cutout argument 'filter'.
       Returns boolean if image metadata filter matches cutout argument filter."""
    co_filt = co_args.get('filter')
    md_filt = metadata.get('filter')
    return (co_filt and md_filt and (co_filt == md_filt))


def extract_metadata (filepath):
    """Extract and return the metadata from the file at the given file path.
       Assumes that the given file path points to a valid, readable FITS file!"""
    timestamp = os.path.getmtime(filepath)
    hdr = fits.getheader(filepath)
    filt = hdr.get('FILTER')
    wcs = WCS(hdr)
    center_pt = wcs.wcs.crval
    corners = wcs.calc_footprint()          # clockwise, starting w/ bottom left corner
    md = { 'timestamp': timestamp, 'wcs': wcs, 'center': center_pt, 'corners': corners }
    if (filt):                              # if image has FILTER header
        md['filter'] = filt.strip()         # save it as metadata
    return md                               # return the metadata dictionary


def fetch_metadata (filepath):
    """Get and return the metadata for the specified file. If the metadata is not in cache,
       try to extract it from the file and add it to the cache.
       Returns the extracted metadata or None, if problems encountered."""
    md = get_metadata(filepath)             # try to get metadata for this file
    if (not md):                            # if metadata not found in cache
        if (fits_file_exists(filepath)):    # then if fits file exists
            md = store_metadata(filepath)   # try to add file metadata to cache
    return md


def get_metadata (filepath):
    """Return the metadata for the given filepath, or None if no metadata is found."""
    return IMAGE_MD_CACHE.get(filepath)


def image_contains (filepath, coords):
    """Tell whether the specified image file contains the specified coordinates or not."""
    position = SkyCoord(coords['ra'], coords['dec'], unit='deg')
    return metadata_contains(fetch_metadata(filepath), position)


def image_corners (filepath):
    """Return a (possibly empty) list of corner coordinate pairs for the specified image."""
    corners = []
    md = fetch_metadata(filepath)           # get/add metadata from file
    if (md):
        corners = md['corners'].tolist()
    return corners


def image_filepath_from_filename (filename, imageDir=IMAGES_DIR):
    """Return a filepath for the given filename in the specified image directory."""
    return os.path.join(imageDir, filename)


def fits_file_exists (filepath, imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    """Tell whether the given filepath names a FITS file in the specified image directory or not."""
    return ( utils.is_fits_filename(filepath, extents) and
             os.path.exists(filepath) and
             os.path.isfile(filepath) )


def is_image_file (filepath):
    """Tell whether the given FITS file contains an image or not"""
    hdr = fits.getheader(filepath)
    return (hdr['SIMPLE'] and (hdr['NAXIS'] == 2))


def list_fits_paths (imageDir=IMAGES_DIR, extents=IMAGE_EXTS, collection=None):
    """Return a list of filepaths for FITS files in the given directory.
       FITS files are identified by the given list of valid file extensions."""
    subdir = imageDir
    if (collection):
        subdir = os.path.join(imageDir, collection)
    return [ fyl for fyl in utils.gen_file_paths(subdir) if (utils.is_fits_filename(fyl, extents)) ]


def match_image (co_args, imageDir=IMAGES_DIR, match_fn=None):
    """Return the filepath of an image, from the specified image directory, which contains
       the specified coordinate arguments and satisfies the (optional) given matching function."""
    position = SkyCoord(co_args['ra'], co_args['dec'], unit='deg')

    for filepath in list_fits_paths(imageDir=imageDir):
        md = fetch_metadata(filepath)
        if (not md):                        # if unable to get metadata
            continue                        # then skip this file

        # if matching function and file fails to match cutout parameters, then skip this file
        if (match_fn and (not match_fn(co_args, md))):
            continue

        # if file contains the position, then return the matching filepath immediately
        if (metadata_contains(md, position)):
            current_app.logger.info("(match_image): MATCHED => {0}".format(filepath))
            return filepath

    return None                             # signal failure to find matching file


def metadata_contains (metadata, position):
    """Use the given image metadata to tell whether the image contains the given position or not.
       Returns True if the position is contained within the image footprint or False otherwise."""
    if (metadata):
        wcs = metadata['wcs']
        return wcs.footprint_contains(position).tolist() # tolist converts numpy bool
    else:
        return False


def put_metadata (filepath, md):
    """Put the given metadata into the cache, keyed by the given filepath."""
    IMAGE_MD_CACHE[filepath] = md


def show_cache ():
    """Return a representation of the image cache."""
    return repr(IMAGE_MD_CACHE)


def store_metadata (filepath, imageDir=IMAGES_DIR):
    """Extract, cache, and return the metadata from the specified file in the specified directory.
       Assumes filepath refers to a valid, readable FITS file in the specified directory.
       Returns the extracted metadata or None, if problems encountered."""
    if (is_image_file(filepath)):
        md = extract_metadata(filepath)
        if (md):
            put_metadata(filepath, md)
        return md
    else:
        return None
