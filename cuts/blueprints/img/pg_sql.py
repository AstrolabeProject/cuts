#
# Class for app to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 12/2/2020.
#   Last Modified: Fix: query_cone, query_coordinates SQL construction and field selection.
#
import sys

import psycopg2
# import psycopg2.sql as sql
# from psycopg2.extras import execute_values

from config.settings import APP_NAME
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.pg_sql_base import PostgreSQLBase


class PostgreSQLManager (PostgreSQLBase):

    DEFAULT_QUERY_FIELDS = [ 'id', 'file_path' ]


    def __init__(self, args={}):
        """
        Constructor for class for app to interact with a PostgreSQL database.
        """
        super().__init__(args)

        self.db_schema_name = args.get('db_schema_name', self.dbconfig.get('db_schema_name'))
        self.sql_img_md_table = args.get('sql_img_md_table', self.dbconfig.get('sql_img_md_table'))


    def clean_table_name (self, schema_name=None, table_name=None):
        """ Return a cleaned schema.table string for use in queries. """
        schema_clean = self.clean_id(schema_name or self.db_schema_name)
        table_clean = self.clean_id(table_name or self.sql_img_md_table)
        return f"{schema_clean}.{table_clean}"


    def image_path_from_id (self, uid=0):
        """
        Return an image path string for the specified ID value. Returns None if the
        indexed record is not present in the table.
        """
        image_table = self.clean_table_name()

        imgq = "SELECT id, file_path FROM {} WHERE id = (%s)".format(image_table)
        fields = self.fetch_row(imgq, [uid])
        ipath = fields[1] if fields else None

        if (self._DEBUG):
            print("(image_path_from_id): => '{}'".format(ipath), file=sys.stderr)

        return ipath


    def image_metadata (self, uid=0, select=None):
        """
        Return a singleton (or empty) list of image metadata fields for the identified image.
        :param select: an optional list of metadata fields to be returned (default ALL fields).
        :return a dictionary of metadata for the image with the specified ID or
                None if no metadata record found for the specified ID.
        """
        image_table = self.clean_table_name()
        fields = self.sql4_selected_fields(select)

        imgq = "SELECT {} FROM {} WHERE id = (%s)".format(fields, image_table)
        rows = self.fetch_rows_2dicts(imgq, [uid])
        imd = rows[0] if rows else None

        if (self._DEBUG):
            print("(image_metadata): => '{}'".format(imd), file=sys.stderr)

        return imd


    def image_metadata_by_path (self, ipath, collection=None, select=None):
        """
        Return the image metadata for the file at the given image path.

        :param ipath: image path of the image whose metadata is desired.
        :param collection: optional name of the image collection to use or all, if None.
        :return a list of dictionaries representing the records from the image metadata table.
        """
        image_table = self.clean_table_name()
        fields = self.sql4_selected_fields(select)

        imgq = "SELECT {} FROM {} WHERE file_path = (%s)".format(fields, image_table)
        qargs = [ipath]

        if (collection is not None):            # list only image paths in given collection
            imgq += " AND obs_collection = (%s)"
            qargs.append(self.clean_id(collection))

        imgq += " ORDER BY id;"

        metadata = self.fetch_rows_2dicts(imgq, qargs)

        if (self._DEBUG):
            print("(image_metadata_by_path): => '{}'".format(metadata), file=sys.stderr)

        return metadata                         # return list of dictionaries


    def image_metadata_by_query (self, collection=None, filt=None, select=None):
        """
        Return a list of selected image metadata fields for images which meet the
        given filter and/or collection criteria.

        :param collection: if specified, restrict the listing to the named image collection.
        :param filt: if specified, restrict the listing to images with the named filter.
        :param select: an optional list of fields to be returned in the query (default ALL fields).

        :return a list of metadata dictionaries for images which contain the specified point.
        """
        image_table = self.clean_table_name()
        fields = self.sql4_selected_fields(select)

        imgq = "SELECT {} FROM {}".format(fields, image_table)
        qargs = []                              # no query arguments yet

        where = False
        if (collection is not None):            # add collection argument to query
            imgq += " WHERE obs_collection = (%s)"
            qargs.append(self.clean_id(collection))
            where = True

        if (filt is not None):
            if (where):
                imgq += " AND"
            else:
                imgq += " WHERE"
                where = True
            imgq += " filter = (%s)"
            qargs.append(self.clean_id(filt))

        imgq += " ORDER BY id;"

        metadata = self.fetch_rows_2dicts(imgq, qargs)

        if (self._DEBUG):
            print("(image_metadata_by_query): => '{}'".format(metadata), file=sys.stderr)

        return metadata


    def list_catalog_tables (self, db_schema=None):
        """
        List available image catalogs from the VOS TAP database.
        NB: Tables are added to the TAP database manually via the DALS addTableToTap script.

        :return a list of catalog names from the TAP schema "tables" table for the selected schema.
        """
        db_schema_name = db_schema or self.db_schema_name

        catq = "SELECT table_name FROM tap_schema.tables WHERE schema_name = (%s);"

        rows = self.fetch_rows(catq, [db_schema_name])
        catalogs = [row[0] for row in rows]     # extract names from row tuples

        if (self._DEBUG):
            print("(list_catalog_tables): => '{}'".format(catalogs), file=sys.stderr)

        return catalogs


    def list_collections (self):
        """
        List all image collections in the metadata database.

        :return a list of collections names from the image metadata table.
        """
        image_table = self.clean_table_name()
        collq = """
            SELECT distinct(obs_collection) FROM {}
            WHERE obs_collection IS NOT NULL;
        """.format(image_table)

        rows = self.fetch_rows(collq, [])
        collections = [row[0] for row in rows]     # extract names from row tuples

        if (self._DEBUG):
            print("(list_collections): => '{}'".format(collections), file=sys.stderr)

        return collections


    def list_filters (self, collection=None):
        """
        List all filters for all images in the metadata database or just those in
        the specified collection.

        :param collection: if specified, restrict the listing to the named image collection.
        :return a list of collections names from the image metadata table.
        """
        image_table = self.clean_table_name()

        if (collection is not None):            # list all image paths
            coll_clean = self.clean_id(collection)
            imgq = """
                SELECT distinct(filter) FROM {}
                WHERE obs_collection = (%s)
                AND filter IS NOT NULL;
            """.format(image_table)
            rows = self.fetch_rows(imgq, [coll_clean])

        else:                                   # list only filters used in given collection
            imgq = """
                SELECT distinct(filter) FROM {}
                WHERE filter IS NOT NULL;
            """.format(image_table)
            rows = self.fetch_rows(imgq, [])

        filts = [row[0] for row in rows]       # extract names from row tuples

        if (self._DEBUG):
            print("(list_filters): => '{}'".format(filts), file=sys.stderr)

        return filts


    def list_image_paths (self, collection=None):
        """
        List file paths for all images in the metadata database or just those in
        the specified collection.

        :param collection: if specified, restrict the listing to the named image collection.
        :return a list of image paths from the image metadata table.
        """
        image_table = self.clean_table_name()

        if (collection is not None):            # list all image paths
            coll_clean = self.clean_id(collection)
            imgq = """
                SELECT distinct(file_path) FROM {}
                WHERE obs_collection = (%s);
            """.format(image_table)
            rows = self.fetch_rows(imgq, [coll_clean])

        else:                                   # list only image paths in given collection
            imgq = """
                SELECT distinct(file_path) FROM {};
            """.format(image_table)
            rows = self.fetch_rows(imgq, [])

        ipaths = [row[0] for row in rows]       # extract names from row tuples

        if (self._DEBUG):
            print("(list_image_paths): => '{}'".format(ipaths), file=sys.stderr)

        return ipaths


    def list_table_names (self, db_schema=None):
        """
        List available tables from the current database.

        :param db_schema: optional name of the DB schema to use.
        :return a list of table_names for the selected schema.
        """
        db_schema_name = db_schema or self.db_schema_name

        tblq = """
            SELECT c.relname as name
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r','p','') AND n.nspname = (%s)
            ORDER by name;
        """

        rows = self.fetch_rows(tblq, [db_schema_name])
        tables = [row[0] for row in rows]     # extract names from row tuples

        if (self._DEBUG):
            print("(list_table_names): => '{}'".format(tables), file=sys.stderr)

        return tables


    def query_cone (self, pt_ra, pt_dec, radius, collection=None, filt=None, select=None):
        """
        List metadata for images containing the given point within the given radius.

        :param collection: if specified, restrict the listing to the named image collection.
        :param filt: if specified, restrict the listing to images with the named filter.
        :param select: an optional list of fields to be returned in the query (default ALL fields).

        :return a list of metadata dictionaries for images which contain the specified point.
        """
        image_table = self.clean_table_name()
        fields = self.sql4_selected_fields(select=select)

        imgq = "SELECT {} FROM {}".format(fields, image_table)
        qargs = []                              # no query arguments yet

        where = False
        if (collection is not None):            # add collection argument to query
            imgq += " WHERE obs_collection = (%s)"
            qargs.append(self.clean_id(collection))
            where = True

        if (filt is not None):
            if (where):
                imgq += " AND"
            else:
                imgq += " WHERE"
                where = True
            imgq += " filter = (%s)"
            qargs.append(self.clean_id(filt))

        imgq += " AND" if where else " WHERE"
        imgq += " q3c_radial_query(s_ra, s_dec, (%s), (%s), (%s))"
        imgq += " ORDER BY id;"

        qargs.extend([pt_ra, pt_dec, radius])

        if (self._DEBUG):
            print(f"(query_cone): query='{imgq}'", file=sys.stderr)

        metadata = self.fetch_rows_2dicts(imgq, qargs)

        if (self._DEBUG):
            print(f"(query_cone): len(metadata): {len(metadata)}", file=sys.stderr)

        return metadata


    def query_coordinates (self, pt_ra, pt_dec, collection=None, filt=None, select=None):
        """
        List metadata for images containing the point specified by the given coordinates and
        the optional collection and filter arguments.

        :param collection: if specified, restrict the listing to the named image collection.
        :param filt: if specified, restrict the listing to images with the named filter.
        :param select: an optional list of fields to be returned in the query (default ALL fields).

        :return a list of metadata dictionaries for images which contain the specified point.
        """
        image_table = self.clean_table_name()
        fields = self.sql4_selected_fields(select)

        imgq = "SELECT {} FROM {}".format(fields, image_table)
        qargs = []                              # no query arguments yet

        where = False
        if (collection is not None):            # add collection argument to query
            imgq += " WHERE obs_collection = (%s)"
            qargs.append(self.clean_id(collection))
            where = True

        if (filt is not None):
            if (where):
                imgq += " AND"
            else:
                imgq += " WHERE"
                where = True
            imgq += " filter = (%s)"
            qargs.append(self.clean_id(filt))

        imgq += " AND" if where else " WHERE"
        imgq += " q3c_poly_query((%s), (%s),"
        imgq += " ARRAY[im_ra1, im_dec1, im_ra2, im_dec2, im_ra3, im_dec3, im_ra4, im_dec4]) = TRUE"
        imgq += " ORDER BY id;"

        qargs.extend([pt_ra, pt_dec])

        if (self._DEBUG):
            print(f"(query_coordinates): query='{imgq}'", file=sys.stderr)

        metadata = self.fetch_rows_2dicts(imgq, qargs)

        if (self._DEBUG):
            print(f"(query_coordinates): len(metadata): {len(metadata)}", file=sys.stderr)

        return metadata
