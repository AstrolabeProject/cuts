#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Begin redo: create class skeleton.
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
        dbconfig = pg_sql.load_sql_db_config(dbconfig_file)


    def __enter__ (self):
        return self


    def __exit__ (self, exc_type, exc_value, traceback):
        self.cleanup()


    def cleanup (self):
        """ Cleanup the current session. """
        pass

