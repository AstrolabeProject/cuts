import os

from flask import current_app, request

from config.settings import FITS_MIME_TYPE, IMAGES_DIR, IMAGE_EXTS

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

# The metadata cache
IMAGE_MD_CACHE = {}


# Clear all entries in the metadata cache.
def clear_cache ():
    IMAGE_MD_CACHE = {}
    # current_app.logger.error("(clear_cache): CACHE: {}".format(IMAGE_MD_CACHE))


# Initialize metadata cache with data from all FITS files in the image directory.
def initialize_cache ():
    clear_cache()
    for filename in list_fits_files():
        store_metadata(filename)
    # current_app.logger.error("(initialize_cache): CACHE: {}".format(IMAGE_MD_CACHE))


# Refresh the metadata cache with data from any new or changed FITS files
# found in the image directory.
def refresh_cache ():
    for filename in list_fits_files():
        md = get_metadata(filename)         # try to get metadata for file
        if (not md):                        # metadata not found in cache
            store_metadata(filename)        # so add it to cache
        else:                               # metadata was found: check if stale
            ctime = md['timestamp']         # timestamp of data in cache
            imagepath = image_filepath_from_filename(filename)
            ftime = os.path.getmtime(imagepath) # modification time on file
            if (ftime > ctime):             # if cache data is stale
                store_metadata(filename)    # update the cache


# Extract and return the metadata from the file at the given file path.
# Assumes that the given file path points to a valid, readable FITS file!
def extract_metadata (filepath):
    timestamp = os.path.getmtime(filepath)
    wcs = WCS(fits.getheader(filepath))
    center_pt = wcs.wcs.crval
    corners = wcs.calc_footprint()          # clockwise, starting w/ bottom left corner
    return { 'wcs': wcs, 'center': center_pt, 'corners': corners }


# Get and return the metadata for the specified file. If the metadata is not in cache,
# try to extract it from the file and add it to the cache.
# Returns the extracted metadata or None, if problems encountered.
def fetch_metadata (filename):
    md = get_metadata(filename)             # try to get metadata for this file
    if (not md):                            # if metadata not found in cache
        if (is_fits_file(filename)):        # then if fits file exists
            md = store_metadata(filename)   # try to add file metadata to cache
    return md


# Return the metadata for the given filename, or None if no metadata is found.
def get_metadata (filename):
    return IMAGE_MD_CACHE.get(filename)


# Tell whether the specified image file contains the specified coordinates or not.
def image_contains (filename, coords):
    imagepath = image_filepath_from_filename(filename)
    position = SkyCoord(coords['ra'], coords['dec'], unit='deg')
    md = get_metadata(filename)
    if (md):
        wcs = md['wcs']
        return wcs.footprint_contains(position).tolist() # tolist converts numpy bool
    else:
        return False


# Return a (possibly empty) list of corner coordinate pairs for the specified image.
def image_corners (filename):
    corners = []
    md = fetch_metadata(filename)           # get/add metadata from file
    if (md):
        corners = md['corners'].tolist()
    return corners


# Return a filepath for the given filename in the specified image directory.
def image_filepath_from_filename (filename, imageDir=IMAGES_DIR):
    return os.path.join(imageDir, filename)


# Tell whether the given filename names a FITS file in the specified image directory or not.
def is_fits_file (filename, imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    filepath = image_filepath_from_filename(filename, imageDir)
    return ( filename.endswith(tuple(extents)) and
             os.path.exists(filepath) and
             os.path.isfile(filepath) )


# Tell whether the given FITS file contains an image or not
def is_image_file (filepath):
    hdr = fits.getheader(filepath)
    return ((hdr['NAXIS'] == 2) and (hdr['EXTEND']))


# Return a list of filepaths for FITS files in the given directory.
# FITS files are identified by the given list of valid file extensions.
def list_fits_files (imageDir=IMAGES_DIR, extents=IMAGE_EXTS):
    return [ fyl for fyl in os.listdir(imageDir) if (fyl.endswith(tuple(extents))) ]


# Put the given metadata into the cache, keyed by the given filename.
def put_metadata (filename, md):
    IMAGE_MD_CACHE[filename] = md


# Extract, cache, and return the metadata from the specified file in the specified directory.
# Assumes filename refers to a valid, readable FITS file in the specified directory.
# Returns the extracted metadata or None, if problems encountered.
def store_metadata (filename, imageDir=IMAGES_DIR):
    imagepath = image_filepath_from_filename(filename, imageDir=imageDir)
    if (is_image_file(imagepath)):
        md = extract_metadata(imagepath)
        if (md):
            put_metadata(filename, md)
        return md
    else:
        return None


#
# Temporary methods
#

# return filename of an image from the specified image directory selected by the given cutout args
def find_image_filename (co_args, imageDir=IMAGES_DIR):
    fyls = {
        "F090W": "goods_s_F090W_2018_08_29.fits",
        "F115W": "goods_s_F115W_2018_08_29.fits",
        "F150W": "goods_s_F150W_2018_08_29.fits",
        "F200W": "goods_s_F200W_2018_08_29.fits",
        "F277W": "goods_s_F277W_2018_08_29.fits",
        "F335M": "goods_s_F335M_2018_08_29.fits",
        "F356W": "goods_s_F356W_2018_08_30.fits",
        "F410M": "goods_s_F410M_2018_08_30.fits",
        "F444W": "goods_s_F444W_2018_08_31.fits"
    }

    # currently, selecting one image based on filter type
    selected = fyls.get(co_args.get('filter'))
    if (not selected):
        return None
    else:
        return selected
