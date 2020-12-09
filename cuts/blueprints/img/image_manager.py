#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Update to use PG manager instance.
#
import os
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from config.settings import FITS_IMAGE_EXTS, FITS_MIME_TYPE, IMAGES_DIR
# import cuts.blueprints.img.utils as utils
from cuts.blueprints.img import exceptions
from cuts.blueprints.img.pg_sql import PostgreSQLManager


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


    def list_collections (self):
        """ Return a list of collection name strings for all image collections. """
        colls = self.pgsql.list_collections()
        colls.sort()
        return colls


    def list_image_paths (self, collection=None):
        """
        Return a list of image path strings for all images or those in the specified collection.
        """
        paths = self.pgsql.list_image_paths(collection=collection)
        paths.sort()
        return paths
