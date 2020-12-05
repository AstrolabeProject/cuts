#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Add method to list image paths. Sort returned lists.
#
import os
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from config.settings import DEFAULT_DBCONFIG_FILEPATH, FITS_IMAGE_EXTS, FITS_MIME_TYPE, IMAGES_DIR
import cuts.blueprints.img.utils as utils
import cuts.blueprints.img.pg_sql as pg_sql
from cuts.blueprints.img import exceptions


class ImageManager:
    """ Class to serve images, metadata, and cutouts from a local database and image files. """

    def __init__ (self, args={}):
        self.args = args                    # save arguments passed to this instance
        self._DEBUG = args.get('debug', False)

        # load the database configuration from a given or default file path
        dbconfig_file = args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        self.dbconfig = pg_sql.load_sql_db_config(dbconfig_file)


    def __enter__ (self):
        return self


    def __exit__ (self, exc_type, exc_value, traceback):
        self.cleanup()


    def cleanup (self):
        """ Cleanup the current session. """
        pass


    def list_collections (self):
        """ Return a list of collection name strings for all image collections. """
        colls = pg_sql.list_collections(self.args, self.dbconfig)
        colls.sort()
        return colls


    def list_image_paths (self, collection=None):
        """
        Return a list of image path strings for all images or those in the specified collection.
        """
        paths = pg_sql.list_image_paths(self.args, self.dbconfig, collection=collection)
        paths.sort()
        return paths
