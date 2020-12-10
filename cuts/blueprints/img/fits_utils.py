#
# Module to provide FITS utility functions for Astrolabe code.
#   Written by: Tom Hicks. 1/26/2020.
#   Last Modified: Port from Image MetaData ToolKit project.
#
import fnmatch
import os

from astropy import wcs
from astropy.time import Time
from astropy.table import Table
from astropy.wcs.utils import proj_plane_pixel_scales

from cuts.blueprints.img.file_utils import is_acceptable_filename, gen_file_paths, validate_file_path
from cuts.blueprints.img.misc_utils import to_JSON


# patterns for identifying FITS and gzipped FITS files
_FITS_PAT = "*.fits"
_GZFITS_PAT = "*.fits.gz"

# size, in bytes, of each FITS file chunk
FITS_BLOCK_SIZE = 2880

# keyword byte string identifying the last (unpadded!) card in a FITS Header
FITS_END_KEY = b'END'

# suffixes for identifying FITS and gzipped FITS files
FITS_EXTENTS = [ '.fits', '.fits.gz' ]

# Common keys to be ignored when reading FITS file header.
# The empty key string is important: it removes any non-Key/Value lines.
FITS_IGNORE_KEYS = [ 'COMMENT', 'HISTORY', '' ]

# MIME type for FITS files
FITS_MIME_TYPE = 'image/fits'

# FITS data type code to name translation table
PIXTYPE_TABLE = {
    8: 'byte', 16: 'short', 32: 'int', 64: 'long', -32: 'float', -64: 'double',
    '8': 'byte', '16': 'short', '32': 'int', '64': 'long', '-32': 'float', '-64': 'double'
}


def bitpix_size (bitpix):
    """
    Return the size in bits for the given FITS header code value from the BITPIX field.
    """
    return abs(int(bitpix))


def fits_file_exists (filepath):
    """ Tell whether the given filepath names an existing, readable FITS file or not. """
    return validate_file_path(filepath, FITS_EXTENTS)


def fits_utc_date (value_str, scale='utc'):
    """
    Return an astropy.time.Time object parsed from the given datetime string using
    the optional time scale.
    """
    # TODO: Better implementation: this will only work for well-formed, complete date strings
    #       and defaults to UTC scale.
    #   see: https://docs.astropy.org/en/stable/time/
    #   see: https://docs.astropy.org/en/stable/api/astropy.time.Time.html
    return Time(value_str)


def gen_fits_file_paths (root_dir):
    """ Generator to yield all FITS files in the file tree under the given root directory. """
    for file_path in gen_file_paths(root_dir):
        if (validate_file_path(file_path, FITS_EXTENTS)):
            yield file_path


def get_column_info (hdus_list, which_hdu=1):
    """
    Return a dictionary of metadata describing the columns of the table in the
    specified HDU. Per Astropy, the returned dictionary contains arrays of metadata,
    each containing values for a particular property for each table column (e.g., name,
    format, unit, bscale, etc).
    """
    col_md = None
    try:
        if (which_hdu < len(hdus_list)):    # if HDU index is in valid range
            col_md = hdus_list[which_hdu].columns.info(output=False)
    except AttributeError:                  # probably wrong HDU was specified
        return None
    return col_md


def get_fields_from_header (header, ignore=FITS_IGNORE_KEYS):
    """
    Return a dictionary of keys and values for the cards in the given FITS header.
    The result dictionary will not contain entries for cards whose keys are
    in the given "ignore list". Note that the result dictionary will contain only the
    last value found for duplicate keys.
    """
    hdrs = dict()
    filtered = [ card for card in header.items() if (card[0] not in ignore) ]
    hdrs.update(filtered)
    return hdrs


def get_header_fields (hdus_list, which_hdu=0, ignore=FITS_IGNORE_KEYS):
    """
    Return a dictionary of keys and values for the cards in the selected HDU
    (default: 0 (the first HDU)) or None, if the given HDU index is out of range.
    The result dictionary will not contain entries for cards whose keys are
    in the given "ignore list". Note that the result dictionary will contain only the
    last value found for duplicate keys.
    """
    if (which_hdu >= len(hdus_list)):       # sanity check
        return None
    header = hdus_list[which_hdu].header
    return get_fields_from_header(header, ignore)


def get_image_corners (wcs):
    """
    Return the image corners as a list, given a valid WCS object, extracted from the image.
    Corners are listed clockwise from the lower left corner.
    """
    return list(wcs.calc_footprint())


def get_image_scale (wcs):
    """
    Return the image scale as a list of projection plane increments corresponding to each axis,
    calculated from the given FITS file WCS information.

    The units of the returned results are the same as the units of cdelt,
    crval, and cd for the celestial WCS and can be obtained by inquiring the
    value of cunit property of the input WCS object.
    """
    return list(proj_plane_pixel_scales(wcs))


def get_metadata_keys (args):
    """
    Return a list of metadata keys to be extracted.

    throws FileNotFoundError is given a non-existant or unreadable filepath.
    """
    keyfile = args.get("keyfile")
    if (keyfile):
        with open(keyfile, "r") as mdkeys_file:
            return mdkeys_file.read().splitlines()
    else:
        return None


def get_table_meta_attribute (table):
    """
    The table attribute 'meta', is a dictionary parsed from the given table's
    headers by Astropy upon reading the table. If present, the "extra" metadata
    usually contains information about the origin of the table.

    This method returns an empty dictionary if no "extra" FITS headers were found
    (i.e., there is no 'meta' attribute attached to the given table).

    :param table: astropy.table.Table
    """
    try:
        meta = table.meta                   # maybe no extra table metadata
    except AttributeError:
        meta = {}
    finally:
        return meta


def get_WCS (ff_hdus_list, which_hdu=0):
    """
    Return a World Coordinate System structure from the header in the specified HDU
    (default: the first HDU) or None, if the given HDU index is out of range.
    """
    if (which_hdu >= len(ff_hdus_list)):    # sanity check
        return None
    return wcs.WCS(ff_hdus_list[which_hdu].header)


def is_catalog_file (ff_hdus_list, which_hdu=1):
    """
    Tell whether the given FITS file is a FITS catalog or not,
    based on a specified HDU (defaults to the first extension).
    Assumes: a catalog HDU will be of type BINTABLE or TABLE:
    """
    return ( (len(ff_hdus_list) > which_hdu) and
             (ff_hdus_list[which_hdu].header.get('XTENSION') in ['BINTABLE', 'TABLE']) )


def is_fits_file (fyl):
    """ Return True if the given file is FITS file, else False. """
    return (fnmatch.fnmatch(fyl, _FITS_PAT) or fnmatch.fnmatch(fyl, _GZFITS_PAT))


def is_fits_filename (filename, extents=FITS_EXTENTS):
    """ Return True if the given filename string names a FITS file, else False. """
    return is_acceptable_filename(filename, extents)


def lookup_pixtype (bitpix, default='UNKNOWN'):
    """
    Return the pixel data type for the given FITS header code value from the BITPIX field.
    Returns default value if the code is not found upon lookup.
    """
    return PIXTYPE_TABLE.get(bitpix, default)


def rows_from_data (data):
    """
    Return a list of rows for the given astropy.io.fits.fitsrec.FITS_rec data.
    Each row in the returned list is a heterogeneous list of values for the row.
    """
    return data.tolist()                    # use numpy.ndarray conversion function


# def table_to_JSON (table, orient='values'):
#     """
#     Return a JSON string of table data from the given astropy.table.Table.
#     The format of the table in the returned JSON is determined by the 'orient'
#     parameter which is passed on to the pandas.to_json method. See:
#     https://pandas.pydata.org/pandas-docs/stable/user_guide/io.html#orient-options
#     This method requires import of Pandas library.
#     """
#     return table.to_pandas().to_json(orient=orient)
