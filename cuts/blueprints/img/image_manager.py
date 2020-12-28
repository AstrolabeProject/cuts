#
# Class to manage images, metadata, and cutouts from an images database and corresponding
# FITS image files found locally on disk.
#
#   Written by: Tom Hicks. 11/14/2019.
#   Last Modified: Refactor: move cutout work here, cleanups.
#
import os
import sys
import pathlib as pl

from flask import current_app, request, send_from_directory

from astropy import units as u
from astropy.io import fits
from astropy.coordinates import SkyCoord
from astropy.nddata import Cutout2D
from astropy.nddata.utils import NoOverlapError, PartialOverlapError
from astropy.wcs import WCS

from config.settings import CUTOUTS_DIR, CUTOUTS_MODE, FITS_IMAGE_EXTS, FITS_MIME_TYPE, IMAGES_DIR
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


    def cleanup (self):
        """ Cleanup the current session. """
        pass


    def fetch_image (self, uid, mimetype=FITS_MIME_TYPE):
        """
        Read and return the image with the specified ID or None, if no such image record found.
        Handles dispatching to fetch methods for different storage devices (e.g., local disk, iRods).
        """
        ipath = self.pgsql.image_path_from_id(uid)
        return self.fetch_image_by_path(ipath, mimetype=mimetype)


    def fetch_image_by_filter (self, filt, collection=None, mimetype=FITS_MIME_TYPE):
        """
        Find and return the most recent image with the specified filter. Handles dispatching
        to fetch methods for different storage devices (e.g., local disk, iRods).
        If no collection is given, then the last image with the specified filter is used.
        """
        filtered = self.pgsql.image_metadata_by_query(collection=collection, filt=filt)
        if (filtered):
            ipath = filtered[0].get('file_path')
            return self.fetch_image_by_path(ipath, mimetype=mimetype)
        return None


    def fetch_image_by_path (self, ipath, mimetype=FITS_MIME_TYPE):
        """
        Directly read and return the image at the specified image path. Handles
        dispatching to fetch methods for different storage devices (e.g., local disk, iRods)
        """
        return self.return_image_at_path(ipath, mimetype=mimetype) if ipath else None


    def get_cutout (self, ipath, co_args, collection=None):
        """
        Return an image cutout, specified by the given cutout arguments.
        """
        co_filename = self.make_cutout_filename(ipath, co_args, collection=collection)
        print(f"CO_FILENAME={co_filename}", file=sys.stderr) # REMOVE LATER
        # if (not self.is_cutout_cached(co_filename)):    # TODO: IMPLEMENT LATER
        co_filename = self.make_cutout_and_save(ipath, co_args, collection=collection)

        return self.return_cutout_with_name(co_filename)  # return the image cutout


    def image_metadata (self, uid, select=None):
        """
        Return an image metadata dictionary for the identified image.
        :param select: an optional list of metadata fields to be returned (default ALL fields).
        :return a singleton list of metadata dictionary for the image with the specified ID or
                an empty list if no metadata record found for the specified ID.
        """
        return self.pgsql.image_metadata(uid, select=select)


    def image_metadata_by_collection (self, collection):
        """
        Return a (possibly empty) list of image metadata dictionaries for all images in
        the specified collection.
        """
        return self.pgsql.image_metadata_by_query(collection=collection)


    def image_metadata_by_path (self, ipath, collection=None):
        """
        Return a (possibly empty) list of image metadata dictionaries for all images with
        the specified image path (which will have different collections).
        If a collection name is specified, the listing is restricted to the named collection.
        """
        return self.pgsql.image_metadata_by_path(ipath, collection=collection)


    def image_metadata_by_filter (self, filt, collection=None):
        """
        Return a (possibly empty) list of image metadata dictionaries for all images with
        the specified filter.
        If a collection name is specified, the listing is restricted to the named collection.
        """
        return self.pgsql.image_metadata_by_query(filt=filt, collection=collection)


    def is_irods_file (self, filepath):
        # TODO: move this method to iRods helper library
        return (filepath and filepath.startswith(IRODS_ZONE_NAME))


    def list_collections (self):
        """ Return a list of collection name strings for all image collections. """
        colls = self.pgsql.list_collections()
        colls.sort()
        return colls


    def list_cutouts (self):
        """ Return a list of image cutout filenames in the cutouts cache directory. """
        return [ fyl for fyl in os.listdir(CUTOUTS_DIR) if os.path.isfile(os.path.join(CUTOUTS_DIR, fyl)) ]


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


    def make_cutout (self, hdu, co_args):
        """
        Make and return an image cutout for the image HDU, using the given cutout parameters.
        """
        wcs = WCS(hdu.header)

        # make the cutout and update its WCS info
        try:
            cutout = Cutout2D(hdu.data, position=co_args['center'], size=co_args['co_size'],
                              wcs=wcs, mode=CUTOUTS_MODE)
        except (NoOverlapError, PartialOverlapError):
            sky = co_args['center']
            errMsg = f"There is no overlap between the reference image and the given center coordinate: {sky.ra.value}, {sky.dec.value} {sky.ra.unit.name} ({sky.frame.name})"
            current_app.logger.error(errMsg)
            raise exceptions.RequestException(errMsg)

        # save cutout image in the FITS HDU and update FITS header with cutout WCS
        hdu.data = cutout.data
        hdu.header.update(cutout.wcs.to_header())

        return cutout


    def make_cutout_and_save (self, ipath, co_args, collection=None):
        """
        Cut out a section of the image at the given image path, using the specifications
        in the give cutout arguments, name the cutout, save it to a file in the cutout
        cache directory, then return the cached cutout filename.
        """
        hdu = fits.open(ipath)[0]
        cutout = self.make_cutout(hdu, co_args)

        # write the cutout to a new FITS file and then return its filename
        co_filename = self.make_cutout_filename(ipath, co_args, collection=collection)
        self.write_cutout(hdu, co_filename)

        return co_filename                  # return the cached cutout filename


    def make_cutout_filename (self, ipath, co_args, collection=None):
        """ Return a filename for the Astropy cutout from info in the given parameters. """
        basename = os.path.splitext(os.path.basename(ipath))[0]
        ra = co_args.get('ra')
        dec = co_args.get('dec')
        size = co_args.get('size')
        units = co_args.get('units').to_string()
        # shape = cutout.shape
        coll = self.pgsql.clean_id(collection) if (collection is not None) else ''
        # return f"{coll}_{basename}__{ra}_{dec}_{shape[0]}x{shape[1]}.fits"
        return f"{coll}_{basename}__{ra}_{dec}_{size}_{units}.fits"


    def query_cone (self, co_args, collection=None, filt=None, select=DEFAULT_SELECT_FIELDS):
        """
        Return a list of image metadata for images which contain a given point
        within a given radius. If an image collection is specified, restrict the search
        to the specified collection.
        :return a possibly empty list of image metadata dictionaries
        """
        ra = co_args.get('ra')
        dec = co_args.get('dec')
        radius = co_args.get('size')
        return self.pgsql.query_cone(ra, dec, radius, collection=collection, filt=filt, select=select)


    def query_image (self, collection=None, filt=None, select=DEFAULT_SELECT_FIELDS):
        """
        Return a list of selected image metadata fields for images which meet the
        given filter and/or collection criteria.

        :param collection: if specified, restrict the listing to the named image collection.
        :param filt: if specified, restrict the listing to images with the named filter.
        :param select: a optional list of fields to be returned in the query (default ALL fields).
        """
        return self.pgsql.query_image(collection=collection, filt=filt, select=select)


    def return_cutout_with_name (self, co_filename, mimetype=FITS_MIME_TYPE):
        """ Return the named cutout file, giving it the specified MIME type. """
        co_filepath = os.path.join(CUTOUTS_DIR, co_filename)
        if (fits_file_exists(co_filepath)):
            return send_from_directory(CUTOUTS_DIR, co_filename, mimetype=mimetype,
                                       as_attachment=True, attachment_filename=co_filename)
        errMsg = f"Image cutout file '{co_filename}' not found in cutouts cache directory"
        current_app.logger.error(errMsg)
        raise exceptions.ServerException(errMsg)


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


    def return_image_at_path (self, ipath, mimetype=FITS_MIME_TYPE):
        """
        Read and return the image at the specified device path. Handles dispatching
        to fetch methods for different storage devices (e.g., local disk, iRods).
        """
        if (self.is_irods_file(ipath)):
            # TODO: IMPLEMENT iRods fetch image
            raise exceptions.ImageNotFound(errMsg)

        else:
            return self.return_image_at_filepath(ipath, mimetype=mimetype)


    def write_cutout (self, hdu, co_filename, overwrite=True):
        """ Write the contents of the given HDU to the named file in the cutouts directory. """
        co_filepath = os.path.join(CUTOUTS_DIR, co_filename)
        hdu.writeto(co_filepath, overwrite=True)
