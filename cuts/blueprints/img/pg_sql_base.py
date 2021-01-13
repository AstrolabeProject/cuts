#
# Base class for common methods to interact with a PostgreSQL database.
#   Written by: Tom Hicks. 12/2/2020.
#   Last Modified: Update for exception refactoring.
#
import configparser
import sys
from string import ascii_letters, digits

import psycopg2
import psycopg2.extras

from config.settings import DEFAULT_DBCONFIG_FILEPATH
import cuts.blueprints.img.exceptions as exceptions
from cuts.blueprints.img.misc_utils import keep_characters


# Restricted set of characters allowed for database identifiers by cleaning function
DB_ID_CHARS = set(ascii_letters + digits + '_')


class ISQLBase ():
    """
    Class defining common methods for managing data in an SQL database.
    """

    def __init__ (self, args={}):
        """
        Constructor for base class to interact with a PostgreSQL database.
        """
        self.args = args                    # save arguments passed to this instance
        self._DEBUG = args.get('debug', False)

        # load the database configuration from a given or default file path
        dbconfig_file = args.get('dbconfig_file') or DEFAULT_DBCONFIG_FILEPATH
        dbconfig = ISQLBase.load_sql_db_config(dbconfig_file)
        self.dbconfig = dbconfig
        self.db_uri = dbconfig.get('db_uri')


    @classmethod
    def load_sql_db_config (clazz, dbconfig_file):
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
            raise exceptions.ServerError(errMsg)

        try:
            dbconfig = dict(config['db_properties'])  # try to fetch DB properties
        except KeyError:
            e1 = 'DB storage specified but no database parameters (db_properties) found'
            errMsg = "{} in DB configuration file '{}'.".format(e1, dbconfig_file)
            raise exceptions.ServerError(errMsg)

        if (dbconfig.get('db_uri') is None):
            e1 = 'DB storage specified but no database URI (db_uri) parameter found'
            errMsg = "{} in DB configuration file '{}'.".format(e1, dbconfig_file)
            raise exceptions.ServerError(errMsg)

        return dbconfig


    def clean_id (self, identifier, allowed=DB_ID_CHARS):
        """
        Clean the given SQL identifier to prevent SQL injection attacks.
        Note: that this method is specifically for simple SQL identifiers and is NOT
        a general solution which prevents SQL injection attacks.
        """
        if (identifier):
            return keep_characters(identifier, allowed)
        else:
            errMsg = "Identifier to be cleaned cannot be empty or None."
            raise exceptions.ServerError(errMsg)


    def execute_sql (self, sql_query_string, sql_values):
        """
        Open a database connection execute the given SQL format string with
        the given SQL values list FOR SIDE EFFECT (i.e. no values are returned).

        :param sql_query_string: a valid Psycopg2 query string. This is similar to a
           standard python template string, BUT NOT THE SAME. See:
           https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        :param sql_values: a list of values to substitute into the query string.
        """
        conn = psycopg2.connect(self.db_uri)
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query_string, sql_values)
        finally:
            conn.close()


    def fetch_row (self, sql_query_string, sql_values):
        """
        Open a database connection and execute the given SQL format string with
        the given SQL values, returning a single query result (a tuple) or None.

        :param sql_query_string: a valid Psycopg2 query string. This is similar to a
            standard python template string, BUT NOT THE SAME. See:
            https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        :param sql_value: a list of values to substitute into the query string.
        """
        conn = psycopg2.connect(self.db_uri)
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query_string, sql_values)
                    row = cursor.fetchone()
        finally:
            conn.close()

        return row


    def fetch_rows (self, sql_query_string, sql_values):
        """
        Open a database connection and execute the given SQL format string with
        the given SQL values, returning a list of tuples, which are the rows of
        the query result.

        :param sql_query_string: a valid Psycopg2 query string. This is similar to a
            standard python template string, BUT NOT THE SAME. See:
            https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        :param sql_value: a list of values to substitute into the query string.
        """
        conn = psycopg2.connect(self.db_uri)
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query_string, sql_values)
                    rows = cursor.fetchall()
        finally:
            conn.close()

        return rows


    def fetch_rows_2dicts (self, sql_query_string, sql_values):
        """
        Open a database connection and execute the given SQL format string with the
        given SQL values, returning a dictionary of attributes, which are the rows of
        the query result.

        :param sql_query_string: a valid Psycopg2 query string. This is similar to a
            standard python template string, BUT NOT THE SAME. See:
            https://www.psycopg.org/docs/usage.html#passing-parameters-to-sql-queries
        :param sql_value: a list of values to substitute into the query string.
        :return a list of dictionaries, one for each result row.
        """
        conn = psycopg2.connect(self.db_uri, cursor_factory=psycopg2.extras.DictCursor)
        try:
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql_query_string, sql_values)
                    rows = cursor.fetchall()
                    rowdicts = [dict(row) for row in rows]  # make array of dictionaries
        finally:
            conn.close()

        return rowdicts
