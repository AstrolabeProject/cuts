#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Add method to get image metadata by filepath.
#
import os
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.wcs import WCS

from config.settings import FITS_IMAGE_EXTS, FITS_MIME_TYPE, IMAGES_DIR
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.fits_utils import fits_file_exists
from cuts.blueprints.img.pg_sql import PostgreSQLManager


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


    def fetch_image (self, filepath, collection=None, mimetype=FITS_MIME_TYPE):
        """
        Find and return the image at the specified path, in the optionally
        specified collection, giving it the specified MIME type. If no collection
        is given, then the first image with the specified path is used.
        """
        if (self.is_irods_file(filepath)):
            # TODO: IMPLEMENT iRods fetch image
            raise exceptions.ImageNotFound(errMsg)

        if (fits_file_exists(filepath)):
            (imageDir, filename) = os.path.split(filepath)
            return send_from_directory(imageDir, filename, mimetype=mimetype,
                                       as_attachment=True, attachment_filename=filename)
        else:
            errMsg = f"Specified image file '{filepath}' not found"
            current_app.logger.error(errMsg)
            raise exceptions.ImageNotFound(errMsg)


    def get_image_metadata (self, filepath, collection=None):
        """
        Find and return the metadata for the image at the specified path, in the
        optionally specified collection. If no collection is given, then the
        first image with the specified path is used.
        """
        return self.pgsql.get_image_metadata(filepath, collection=collection)


    def is_irods_file (self, filepath):
        # TODO: move this method to iRods helper library
        return (filepath and filepath.startswith(IRODS_ZONE_NAME))


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
