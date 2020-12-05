#
# Module to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 12/2/2020.
#   Last Modified: Add clean_table and list_image_paths methods.
#
import configparser
import sys
from string import ascii_letters, digits

import psycopg2
# from psycopg2.extras import execute_values

from config.settings import APP_NAME
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.misc_utils import keep_characters


# Restricted set of characters allowed for database identifiers by cleaning function
DB_ID_CHARS = set(ascii_letters + digits + '_')


def load_sql_db_config (dbconfig_file):
    """
    Load the database configuration from the given filepath. Returns a dictionary
    of database configuration parameters.
    """
    try:
        config = configparser.ConfigParser(interpolation=configparser.ExtendedInterpolation(),
                                           strict=False, empty_lines_in_values=False)
        config.read_file(open(dbconfig_file))  # try to read the DB config file
    except FileNotFoundError:
        errMsg = "DB configuration file '{}' not found or not readable.".format(dbconfig_file)
        raise exceptions.ServerException(errMsg)

    try:
        dbconfig = dict(config['db_properties'])  # try to fetch DB properties
    except KeyError:
        e1 = 'DB storage specified but no database parameters (db_properties) found'
        errMsg = "{} in DB configuration file '{}'.".format(e1, dbconfig_file)
        raise exceptions.ServerException(errMsg)

    if (dbconfig.get('db_uri') is None):
        e1 = 'DB storage specified but no database URI (db_uri) parameter found'
        errMsg = "{} in DB configuration file '{}'.".format(e1, dbconfig_file)
        raise exceptions.ServerException(errMsg)

    return dbconfig


def clean_id (identifier, allowed=DB_ID_CHARS):
    """
    Clean the given SQL identifier to prevent SQL injection attacks.
    Note: that this method is specifically for simple SQL identifiers and is NOT
    a general solution which prevents SQL injection attacks.
    """
    if (identifier):
        return keep_characters(identifier, allowed)
    else:
        errMsg = "Identifier to be cleaned cannot be empty or None."
        raise errors.ProcessingError(errMsg)


def clean_table (dbconfig, schema_name=None, table_name=None):
    """ Return a cleaned schema.table string for use in queries. """
    schema_clean = clean_id(schema_name or dbconfig.get('db_schema_name'))
    table_clean = clean_id(table_name or dbconfig.get('sql_img_md_table'))
    return f"{schema_clean}.{table_clean}"


def execute_sql (dbconfig, sql_query_string, sql_values):
    """
    Open a database connection using the given DB configuration and execute the given SQL
    format string with the given SQL values list FOR SIDE EFFECT (i.e. no values are returned).

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    :param sql_values: a list of values to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query_string, sql_values)
    finally:
        conn.close()


def fetch_rows (dbconfig, sql_query_string, sql_values):
    """
    Open a database connection using the given DB configuration and execute the given SQL
    format string with the given SQL values, returning a list of tuples, which are the
    rows of the query result.

    :param dbconfig: dictionary containing database parameters used by this method: db_uri
        Note: the given database configuration must contain a valid 'db_uri' string.
    :param sql_query_string: a valid Psycopg2 query string. This is similar to a
        standard python template string, BUT NOT THE SAME. See:
        https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
    :param sql_value: a list of values to substitute into the query string.
    """
    db_uri = dbconfig.get('db_uri')
    conn = psycopg2.connect(db_uri)
    try:
        with conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query_string, sql_values)
                rows = cursor.fetchall()
    finally:
        conn.close()

    return rows


def list_catalog_tables (args, dbconfig, db_schema=None):
    """
    List available image catalogs from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of catalog names from the TAP schema "tables" table for the selected schema.
    """
    db_schema_name = db_schema or dbconfig.get('db_schema_name')

    catq = "SELECT table_name FROM tap_schema.tables WHERE schema_name = (%s);"

    rows = fetch_rows(dbconfig, catq, [db_schema_name])
    catalogs = [row[0] for row in rows]     # extract names from row tuples

    if (args.get('debug')):
        print("(list_catalog_tables): => '{}'".format(catalogs), file=sys.stderr)

    return catalogs


def list_collections (args, dbconfig):
    """
    List available image collections from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of collections names from the image metadata table.
    """
    image_table = clean_table(dbconfig)
    collq = "SELECT distinct(obs_collection) FROM {};".format(image_table)

    rows = fetch_rows(dbconfig, collq, [])
    collections = [row[0] for row in rows]     # extract names from row tuples

    if (args.get('debug')):
        print("(list_collections): => '{}'".format(collections), file=sys.stderr)

    return collections


def list_image_paths (args, dbconfig, collection=None):
    """
    List available image collections from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :param collection: name of the image collection to list or list all, if None.
    :return a list of collections names from the image metadata table.
    """
    image_table = clean_table(dbconfig)

    if (collection is not None):            # list all image paths
        coll_clean = clean_id(collection)
        imgq = """
            SELECT distinct(file_path) FROM {}
            WHERE obs_collection = (%s)
            ORDER BY file_path ASC;
        """.format(image_table)
        rows = fetch_rows(dbconfig, imgq, [coll_clean])

    else:                                   # list only image paths in given collection
        imgq = """
            SELECT distinct(file_path) FROM {}
            ORDER BY file_path ASC;
        """.format(image_table)
        rows = fetch_rows(dbconfig, imgq, [])

    ipaths = [row[0] for row in rows]       # extract names from row tuples

    if (args.get('debug')):
        print("(list_image_paths): => '{}'".format(ipaths), file=sys.stderr)

    return ipaths


def list_table_names (args, dbconfig, db_schema=None):
    """
    List available tables from the VOS database.

    :param args: dictionary containing context arguments used by this method: debug
    :param dbconfig: dictionary containing database parameters used by this method: db_uri
    :return a list of table_names for the selected schema.
    """
    db_schema_name = db_schema or dbconfig.get('db_schema_name')

    tblq = """
        SELECT c.relname as name
        FROM pg_catalog.pg_class c
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
        WHERE c.relkind IN ('r','p','') AND n.nspname = (%s)
        ORDER by name;
    """

    rows = fetch_rows(dbconfig, tblq, [db_schema_name])
    tables = [row[0] for row in rows]     # extract names from row tuples
    if (args.get('debug')):
        print("(pg_sql.list_table_names): => '{}'".format(tables), file=sys.stderr)

    return tables
