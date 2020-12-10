#
# Class to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 12/2/2020.
#   Last Modified: Redo as class. Refactor out common methods to base.
#
import sys

import psycopg2
# from psycopg2.extras import execute_values

from config.settings import APP_NAME
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.i_sql import ISQLBase


class PostgreSQLManager (ISQLBase):

    DEFAULT_SCHEMA_NAME = 'sia'
    DEFAULT_SQL_IMAGE_MD_TABLE = 'jwst'


    def __init__(self, args={}):
        """
        Constructor for class to interact with a PostgreSQL database.
        """
        super().__init__(args)

        self.db_schema_name = self.dbconfig.get('db_schema_name', self.DEFAULT_SCHEMA_NAME)
        self.sql_img_md_table = self.dbconfig.get('sql_img_md_table', self.DEFAULT_SQL_IMAGE_MD_TABLE)


    def clean_table_name (self, schema_name=None, table_name=None):
        """ Return a cleaned schema.table string for use in queries. """
        schema_clean = self.clean_id(schema_name or self.db_schema_name)
        table_clean = self.clean_id(table_name or self.sql_img_md_table)
        return f"{schema_clean}.{table_clean}"


    def list_catalog_tables (self, db_schema=None):
        """
        List available image catalogs from the VOS database.

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
        List available image collections from the VOS database.

        :return a list of collections names from the image metadata table.
        """
        image_table = self.clean_table_name()
        collq = "SELECT distinct(obs_collection) FROM {};".format(image_table)

        rows = self.fetch_rows(collq, [])
        collections = [row[0] for row in rows]     # extract names from row tuples

        if (self._DEBUG):
            print("(list_collections): => '{}'".format(collections), file=sys.stderr)

        return collections


    def list_image_paths (self, collection=None):
        """
        List available image collections from the VOS database.

        :param collection: name of the image collection to list or list all, if None.
        :return a list of collections names from the image metadata table.
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
            print("(i_sql.list_table_names): => '{}'".format(tables), file=sys.stderr)

        return tables