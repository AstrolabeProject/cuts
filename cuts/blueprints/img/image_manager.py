#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Rename *by_filename methods. Add *by_filter stubs. Add return_image_at_filepath.
#
import os
import sys
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from config.settings import FITS_IMAGE_EXTS, FITS_MIME_TYPE, IMAGES_DIR
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.fits_utils import fits_file_exists
from cuts.blueprints.img.pg_sql import PostgreSQLManager


DEFAULT_SELECT_FIELDS = [ 'id', 's_ra', 's_dec', 'file_name', 'file_path', 'obs_collection' ]

IRODS_ZONE_NAME = 'iplant'                  # TODO: pull from irods env file

class ImageManager ():
    """ Class to serve images, metadata, and cutouts from a local database and image files. """

    def __init__ (self, args={}):
        self.args = args                      # save arguments passed to this instance
        self._DEBUG = args.get('debug', False)
        self.pgsql = PostgreSQLManager(args)  # create a DB manager


    def __enter__ (self):
        return self


    def __exit__ (self, exc_type, exc_value, traceback):
        self.cleanup()


    def cleanup (self):
        """ Cleanup the current session. """
        pass


    def fetch_image_by_filepath (self, filepath, mimetype=FITS_MIME_TYPE):
        """
        Directly read and return the image at the specified device path. Handles
        dispatching to fetch methods for different storage devices (e.g., local disk, iRods)
        """
        if (self.is_irods_file(filepath)):
            # TODO: IMPLEMENT iRods fetch image
            raise exceptions.ImageNotFound(errMsg)
        else:
            return self.return_image_at_filepath(filepath, mimetype=mimetype)


    def fetch_image_by_filter (self, filt, collection=None, mimetype=FITS_MIME_TYPE):
        """
        Find and return the most recent image with the specified filter. Handles dispatching
        to fetch methods for different storage devices (e.g., local disk, iRods).
        If no collection is given, then the last image with the specified filter is used.
        """
        # TODO: IMPLEMENT LATER
        # with_filter = self.pgsql.query_by_filter
        # if (with_filter):
        #     filepath = with_filter[0].get('file_path')
        #     # TODO: check for empty filepath
        #     return self.return_image_at_filepath(filepath, mimetype=mimetype)
        return None                         # TODO: IMPLEMENT LATER


    def image_metadata_by_filepath (self, filepath, collection=None):
        """
        Find and return the metadata for the image at the specified path, in the
        optionally specified collection. If no collection is given, then the
        first image with the specified path is used.
        """
        return self.pgsql.image_metadata_by_filepath(filepath, collection=collection)


    def image_metadata_by_filter (self, filt, collection=None):
        """
        Find and return the metadata for the most recent image with the specified filter.
        If no collection is given, then the most recent image with the specified filter is used.
        """
        # TODO: IMPLEMENT LATER
        # return self.pgsql.image_metadata_by_filter(filt, collection=collection)
        return []                           # TODO: IMPLEMENT LATER


    def is_irods_file (self, filepath):
        # TODO: move this method to iRods helper library
        return (filepath and filepath.startswith(IRODS_ZONE_NAME))


    def list_collections (self):
        """ Return a list of collection name strings for all image collections. """
        colls = self.pgsql.list_collections()
        colls.sort()
        return colls


    def list_filters (self, collection=None):
        """
        Return a list of filter names for all images or those in the specified collection.
        """
        filts = self.pgsql.list_filters(collection=collection)
        filts.sort()
        return filts


    def list_image_paths (self, collection=None):
        """
        Return a list of image path strings for all images or those in the specified collection.
        """
        paths = self.pgsql.list_image_paths(collection=collection)
        paths.sort()
        return paths


    def query_cone (self, co_args, collection=None, select=DEFAULT_SELECT_FIELDS):
        """
        Return a list of image metadata for images which contain a given point
        within a given radius. If an image collection is specified, restrict the search
        to the specified collection.
        """
        ra = co_args.get('ra')
        dec = co_args.get('dec')
        radius = co_args.get('size')        # radius of cone in degrees required

        if (ra and dec and radius):
            return self.pgsql.query_cone(ra, dec, radius, collection=collection, select=select)

        else:
            errMsg = "'ra', 'dec', and a radius size (one of 'radius', 'sizeDeg', 'sizeArcMin', or 'sizeArcSec') must be specified."
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)


    def return_image_at_filepath (self, filepath, mimetype=FITS_MIME_TYPE):
        """ Return the image file at the specified file path, giving it the specified MIME type. """
        if (fits_file_exists(filepath)):
            (imageDir, filename) = os.path.split(filepath)
            return send_from_directory(imageDir, filename, mimetype=mimetype,
                                       as_attachment=True, attachment_filename=filename)
        else:
            errMsg = f"Specified image file '{filepath}' not found"
            current_app.logger.error(errMsg)
            raise exceptions.ImageNotFound(errMsg)
