#
# Utilities for argument parsing and validataion.
#
#   Written by: Tom Hicks. 12/28/2020.
#   Last Modified: Fix: explicitly import current_app.
#
from flask import current_app

from astropy import units as u
from astropy.coordinates import SkyCoord

from cuts.blueprints.img import exceptions


def parse_collection_arg (args, required=False):
    """
    Parse out the collection argument, returning the collection name string or None,
    if no collection argument given.
    :raises: RequestException if no collection given and the required flag is True.
    """
    coll = args.get('collection', args.get('coll'))
    if ((coll is None) or (not coll.strip())):    # if no collection or empty collection
        if (required):
            errMsg = "A collection name must be specified, via the 'collection' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        else:
            return None
    return coll.strip()


def parse_coordinate_args (args):
    """ Parse, convert, and check the given coordinate arguments, returning a dictionary
        of coordinate arguments. """
    co_args = {}

    raStr = args.get('ra')
    if (not raStr):
        errMsg = "Right ascension must be specified, via the 'ra' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        ra = float(raStr)
        co_args['ra'] = ra

    decStr = args.get('dec')
    if (not decStr):
        errMsg = "Declination must be specified, via the 'dec' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)
    else:
        dec = float(decStr)
        co_args['dec'] = dec

    frame = args.get('frame', 'icrs')       # get optional coordinate reference system

    co_args['center'] = SkyCoord(ra=ra*u.degree, dec=dec*u.degree, frame=frame)

    return co_args                          # return parsed, converted cutout arguments


def parse_cutout_args (args, required=False):
    """ Parse, convert, and check the given arguments, returning a dictionary
        of cutout arguments. Any arguments needed by cutout routines will be passed
        through to the return dictionary.
    """
    co_args = parse_cutout_size(args, required=required)  # first, get cutout size parameters
    co_args.update(parse_coordinate_args(args))  # add coordinate parameters
    return co_args                               # return parsed, converted cutout arguments


def parse_cutout_size (args, required=False):
    """ Parse, convert, and check the given cutout size arguments, return a dictionary of
        the size arguments. No returned cutout size signals that the whole image is desired. """
    co_args = {}                            # dictionary to hold parsed fields

    # read and parse a size specification in arc minutes or degrees
    sizeArcMinStr = args.get('sizeArcMin')
    sizeDegStr = args.get('sizeDeg', args.get('radius'))  # allow alternate radius keyword
    sizeArcSecStr = args.get('sizeArcSec')

    if (sizeArcMinStr):                     # prefer units in arc minutes
        co_args['units'] = u.arcmin
        co_args['size'] = float(sizeArcMinStr)
    elif (sizeDegStr):                      # alternatively in degrees
        co_args['units'] = u.deg
        co_args['size'] = float(sizeDegStr)
    elif (sizeArcSecStr):                   # or in arc seconds
        co_args['units'] = u.arcsec
        co_args['size'] = float(sizeArcSecStr)

    if (co_args.get('size') is None):       # if no size given
        if (required):                      # if size argument required
            errMsg = "A radius size (one of 'radius', 'sizeDeg', 'sizeArcMin', or 'sizeArcSec') must be specified."
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        return co_args                      # not required: return empty dictionary

    # got a size: make a scalar Quantity from the size and units, if possible
    co_args['co_size'] = u.Quantity(co_args['size'], co_args['units'])
    return co_args                          # return parsed, converted cutout arguments


def parse_filter_arg (args, required=False):
    """
    Parse out the filter argument, returning the filter name string or None.
    :raises: RequestException if no filter given and the required flag is True.
    """
    filt = args.get('filter')
    if ((filt is None) or (not filt.strip())):    # if no filter or empty filter
        if (required):
            errMsg = "An image filter must be specified, via the 'filter' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        else:
            return None
    return filt.strip()


def parse_id_arg (args, required=True):
    """
    Parse out the unique ID argument, returning the ID or None, if no ID
    argument is given or if the ID is not covertible to a positive integer > 0.
    :raises: RequestException if no ID given and the required flag is True.
    """
    uid = args.get('id')
    if (uid is not None):
        try:
            num = int(uid)
            if (num > 0):
                return num
        except ValueError:
            pass                            # drop through to error

    if (not required):
        return None
    else:
        errMsg = "A record ID must be specified, via the 'id' argument"
        current_app.logger.error(errMsg)
        raise exceptions.RequestException(errMsg)


def parse_ipath_arg (args, required=False):
    """
    Parse out the image path argument, returning the image path string or None.
    :raises: RequestException if no path given and the required flag is True.
    """
    ipath = args.get('path')
    if ((ipath is None) or (not ipath.strip())):    # if no path or empty path
        if (required):
            errMsg = "A valid image path must be specified, via the 'path' argument"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)
        else:
            return None
    return ipath.strip()
