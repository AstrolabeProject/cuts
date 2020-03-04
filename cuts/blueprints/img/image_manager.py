#
# Module to manage an in-memory image cache containing metadata from
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Catch exceptions on bad FITS files.
#
import os
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from config.settings import FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS

from cuts.blueprints.img import exceptions
import cuts.blueprints.img.utils as utils


# The metadata cache
IMAGE_MD_CACHE = {}


def clear_cache ():
    """ Clear all entries in the metadata cache. """
    IMAGE_MD_CACHE.clear()
    # current_app.logger.error("(clear_cache): CACHE: {}".format(IMAGE_MD_CACHE))


def initialize_cache ():
    """ Initialize metadata cache with data from all FITS files in the image directory. """
    clear_cache()
    for filepath in list_fits_paths():
        store_metadata(filepath)
    # current_app.logger.error("(initialize_cache): CACHE: {}".format(IMAGE_MD_CACHE))


def refresh_cache ():
    """ Refresh the metadata cache with data from any new or changed FITS files
        found in the image directory. """
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
    """ A matching function to match images with filters by cutout argument 'filter'.
        Returns boolean if image metadata filter matches cutout argument filter. """
    co_filt = co_args.get('filter', False)
    md_filt = metadata.get('filter', False)
    return (co_filt and md_filt and (co_filt == md_filt))


def cache_key_from_metadata (metadata):
    """ Return the cache key for an entry from the given metadata or None, if unable to. """
    cache_key = metadata.get('filepath')
    return cache_key if cache_key else None  # all 'falsey' entries mapped to failure


def collection_from_dirpath (dirpath, image_dir=IMAGES_DIR):
    """ Return a collection name string, or the empty string, from the given directory path.
        The given directory path must be a subpath of the specified images root directory.
    """
    try:
        rpath = pl.PurePath(dirpath).relative_to(image_dir) # remove the images root directory
    except ValueError:
        return ''
    return os.sep.join(list(rpath.parts))


def collection_from_filepath (filepath, image_dir=IMAGES_DIR):
    """ Return a collection name string, or the empty string, from the given filepath.
        The given filepath must be a subpath of the specified images root directory.
    """
    try:
        rpath = pl.PurePath(filepath).relative_to(image_dir) # remove the images root directory
    except ValueError:
        return ''
    coll_parts = list(rpath.parts)[:-1]     # drop the filename
    return os.sep.join(coll_parts)


def extract_metadata (filepath, header=None):
    """ Extract and return the metadata from the file at the given file path.
        Assumes that the given file path points to a valid, readable FITS image file! """
    if (not header):
        header = fits.getheader(filepath)

    wcs = WCS(header)
    center_pt = wcs.wcs.crval
    corners = wcs.calc_footprint()          # clockwise, starting w/ bottom left corner

    timestamp = os.path.getmtime(filepath)
    md = { 'filepath': filepath, 'timestamp': timestamp,
           'wcs': wcs, 'center': center_pt, 'corners': corners }

    collection = collection_from_filepath(filepath)
    if (collection):                        # if image is in a collection
        md['collection'] = collection       # save collection name in metadata

    filt = header.get('FILTER')
    if (filt):                              # if image has FILTER header
        md['filter'] = filt.strip()         # save it as metadata

    return md                               # return the metadata dictionary


def fetch_metadata (filepath):
    """ Get and return the metadata for the specified file. If the metadata is not in cache,
        try to extract it from the file and add it to the cache.
        Returns the extracted metadata or None, if problems encountered.
    """
    md = get_metadata(filepath)             # try to get metadata for this file
    if (not md):                            # if metadata not found in cache
        if (fits_file_exists(filepath)):    # then if fits file exists
            md = store_metadata(filepath)   # try to add file metadata to cache
    return md


def fits_file_exists (filepath):
    """ Tell whether the given filepath names a FITS file or not. """
    return ( utils.is_fits_filename(filepath, IMAGE_EXTS) and
             os.path.exists(filepath) and
             os.path.isfile(filepath) )


def gen_collection_names (image_dir=IMAGES_DIR):
    """ Generator to yield all collection names: subdirectories of the images root directory. """
    # (_, dirs, _) = next(os.walk(IMAGES_DIR, followlinks=True)) # this does depth 1 only
    for dirpath, _, _ in os.walk(image_dir, followlinks=True):
        dir_path = collection_from_dirpath(dirpath, image_dir)
        if (dir_path):                      # skip empty entries
            yield dir_path


def get_metadata (filepath):
    """ Return the metadata for the given filepath, or None if no metadata is found. """
    return IMAGE_MD_CACHE.get(filepath)


def image_contains (filepath, coords):
    """ Tell whether the specified image file contains the specified coordinates or not. """
    position = SkyCoord(coords['ra'], coords['dec'], unit='deg', frame=coords.get('frame','icrs'))
    return metadata_contains(fetch_metadata(filepath), position)


def image_corners (filepath):
    """ Return a (possibly empty) list of corner coordinate pairs for the specified image. """
    corners = []
    md = fetch_metadata(filepath)           # get/add metadata from file
    if (md):
        corners = md.get('corners').tolist()
    return corners


def image_dir_from_collection (collection=None, image_dir=IMAGES_DIR):
    """ Return a directory path for the given collection in the specified image directory. """
    return os.path.join(image_dir, collection) if collection else image_dir


def is_image_file (filepath):
    """ Tell whether the given FITS file contains an image or not. """
    try:
        return is_image_header(fits.getheader(filepath))
    except:
        return False


def is_image_header (header):
    """ Tell whether the given FITS header signals a FITS image file or not. """
    return (header.get('SIMPLE') and (header.get('NAXIS') == 2))


def list_collections ():
    """ Return a list of collection name strings for collections of the images directory. """
    return [ cname for cname in gen_collection_names() ]


def list_fits_paths (collection=None):
    """ Return a list of filepaths for FITS files in the image directory or a sub-collection.
        FITS files are identified by the given list of valid file extensions. """
    imageDir = image_dir_from_collection(collection)
    return [ fyl for fyl in utils.gen_file_paths(imageDir) if (utils.is_fits_filename(fyl, IMAGE_EXTS)) ]


def match_image (co_args, collection=None, match_fn=None):
    """ Return the filepath of an image, from the specified image directory, which contains
        the specified coordinate arguments and satisfies the (optional) given matching function.
    """
    position = SkyCoord(co_args['ra'], co_args['dec'], unit='deg', frame=co_args.get('frame','icrs'))

    for filepath in list_fits_paths(collection=collection):
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
    """ Use the given image metadata to tell whether the image contains the given position or not.
        Returns True if the position is contained within the image footprint or False otherwise. """
    if (metadata):
        wcs = metadata.get('wcs')
        if (wcs):
            return wcs.footprint_contains(position).tolist() # tolist converts numpy bool
        else:
            return False
    else:
        return False


def put_metadata (md):
    """ Put the given metadata into the cache, keyed by the cache_key computed from the metadata.
        Returns a boolean to signal success or failure.
    """
    cache_key = cache_key_from_metadata(md)
    if (cache_key):
        IMAGE_MD_CACHE[cache_key] = md
        return True
    else:
        errMsg = "Unable to get image cache key from metadata: {0}".format(md)
        current_app.logger.error(errMsg)
        return False


def return_image (filepath, collection=None, mimetype=FITS_MIME_TYPE):
    """ Return the specified image file, giving it the specified MIME type. """
    if (fits_file_exists(filepath)):
        (imageDir, filename) = os.path.split(filepath)
        return send_from_directory(imageDir, filename, mimetype=mimetype,
                                   as_attachment=True, attachment_filename=filename)
    errMsg = "Specified image file '{0}' not found".format(filepath)
    current_app.logger.error(errMsg)
    raise exceptions.ImageNotFound(errMsg)


def show_cache ():
    """ Return a representation of the image cache. """
    return repr(IMAGE_MD_CACHE)


def store_metadata (filepath):
    """ Extract, cache, and return the metadata from the file at the given filepath.
        Assumes filepath refers to a valid, readable FITS file.
        Returns the extracted metadata or None, if problems encountered.
    """
    if (utils.is_fits_filename(filepath, IMAGE_EXTS)):
        try:
            hdr = fits.getheader(filepath)
            if (is_image_header(hdr)):
                md = extract_metadata(filepath, header=hdr)
                if (md):
                    put_metadata(md)
                    return md
                else:
                    return None
        except:
            return None
    else:
        return None
