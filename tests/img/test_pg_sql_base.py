# Tests for the PostgreSQL base class.
#   Written by: Tom Hicks. 1/13/2021.
#   Last Modified: Initial creation.
#
import pytest

from cuts.blueprints.img.exceptions import ImageNotFound, RequestException, ServerError, NotYetImplemented
from cuts.blueprints.img.pg_sql_base import PostgreSQLBase
from tests import TEST_RESOURCES_DIR, TEST_DBCONFIG_FILEPATH


class TestPostgreSQLBase(object):

    test_args = {
        'debug': True,
        'dbconfig_file': TEST_DBCONFIG_FILEPATH
    }

    dbconfig_tstfyl = TEST_DBCONFIG_FILEPATH
    empty_dbconfig_tstfyl   = f"{TEST_RESOURCES_DIR}/test-dbconfig-empty.ini"
    noprops_dbconfig_tstfyl = f"{TEST_RESOURCES_DIR}/test-dbconfig-no-props.ini"
    nouri_dbconfig_tstfyl   = f"{TEST_RESOURCES_DIR}/test-dbconfig-no-uri.ini"
    nosuch_tstfyl           = f"{TEST_RESOURCES_DIR}/NOSUCHFILE"

    args = { 'debug': True, 'verbose': True, 'TOOL_NAME': 'TestPostgreSQLBase' }


    # base = PostgreSQLBase(test_args)          # instance of class under tests


    def test_load_sql_db_config_bad(self):
        with pytest.raises(ServerError, match='not found or not readable'):
            PostgreSQLBase.load_sql_db_config(self.nosuch_tstfyl)


    def test_load_sql_db_config_no_props(self):
        with pytest.raises(ServerError, match='no database parameters .* found'):
            PostgreSQLBase.load_sql_db_config(self.noprops_dbconfig_tstfyl)


    def test_load_sql_db_config_empty(self):
        with pytest.raises(ServerError, match='no database parameters .* found'):
            PostgreSQLBase.load_sql_db_config(self.empty_dbconfig_tstfyl)


    def test_load_sql_db_config_no_uri(self):
        with pytest.raises(ServerError, match='no database URI .* found'):
            PostgreSQLBase.load_sql_db_config(self.nouri_dbconfig_tstfyl)


    def test_load_sql_db_config(self):
        dbconf = PostgreSQLBase.load_sql_db_config(TEST_DBCONFIG_FILEPATH)
        print(dbconf)
        assert dbconf is not None
        assert len(dbconf) >= 7               # specific to this test file
